#### OCPM REPORT ANALYSIS ######################################################

source("R/00_setup.R")
library(pdftools)
library(tidytext)
library(stm)
library(ggthemes)
library(textcat)
library(furrr)
plan(multisession)

result <- qs::qread("output/result.qs")


# Import PDFs -------------------------------------------------------------

subs <-
  result |> 
  rowwise() |> 
  mutate(citizen = list(
    str_which(headings, "Mémoires|Opinions|Présentations"))) |> 
  ungroup() |> 
  mutate(dl = pmap(list(id, title, citizen), \(id, title, citizen) {
    list.files(path = paste0("pdf/", id, "_", title), 
               pattern = paste0("^", paste(citizen, collapse = "|"), "-"),
               full.names = TRUE) |> 
      str_subset("pdf$")
  }))

text_sub_raw <- suppressWarnings({
  pmap_dfr(list(x = subs$id, y = subs$title, z = subs$dl), \(x, y, z) tibble(
    id = x,
    doc_id = z |> 
      str_remove(paste0("pdf/", x, "_", y, "/")) |> 
      str_remove(".pdf$"),
    text = map(z, pdftools::pdf_text))) |>
    unnest(text)
  })
  

# Tokenize texts ----------------------------------------------------------

text_sub <- 
  text_sub_raw |> 
  unnest_tokens(word, text) |> 
  mutate(word = if_else(str_detect(word, "’|'|‘"), 
                        str_extract(word, ".+(?=(’|'|‘))"), word)) |> 
  filter(!str_detect(word, "\\d")) |> 
  filter(!str_detect(word, "\\.com|\\.ca")) |> 
  filter(str_detect(word, "[:alpha:]"))

bigram_sub <- 
  text_sub_raw |> 
  unnest_tokens(word, text, token = "ngrams", n = 2) |>  
  filter(!is.na(word)) |> 
  separate(word, c("word_1", "word_2"), sep = " ") |> 
  filter(!str_detect(word_1, "\\d"), !str_detect(word_2, "\\d")) |> 
  filter(!str_detect(word_1, "\\.com|\\.ca"), 
         !str_detect(word_2, "\\.com|\\.ca")) |> 
  filter(str_detect(word_1, "[:alpha:]"), str_detect(word_2, "[:alpha:]"))


# Detect language and only keep French ------------------------------------

langs <- 
  text_sub |> 
  group_by(id, doc_id) |> 
  summarize(word = paste(word, collapse = " "), .groups = "drop") |> 
  mutate(lang = textcat(word)) |> 
  select(-word)
  
text_sub <-
  text_sub |> 
  left_join(langs, by = c("id", "doc_id")) |> 
  filter(lang == "french") |> 
  select(-lang)

bigram_sub <- 
  bigram_sub |> 
  left_join(langs, by = c("id", "doc_id")) |> 
  filter(lang == "french") |> 
  select(-lang)


# Remove stop words -------------------------------------------------------

text_sub <- 
  text_sub |> 
  anti_join(stop_words_fr, by = "word") |> 
  anti_join(stop_words, by = "word")

bigram_sub <- 
  bigram_sub |> 
  anti_join(stop_words_fr, by = c("word_1" = "word")) |> 
  anti_join(stop_words_fr, by = c("word_2" = "word")) |> 
  anti_join(stop_words, by = c("word_1" = "word")) |> 
  anti_join(stop_words, by = c("word_2" = "word"))

stop_words_mtl <- 
  result |> 
  pull(title) |> 
  str_split("-") |> 
  unlist() |> 
  unique() |> 
  c(text_sub |> 
      count(word, sort = TRUE) |> 
      slice(1:20) |> 
      pull(word)) |> 
  c("grâce", "côte", "hubert", "villeray", "rené", "lévesque", "hochelaga",
    "mercier", "kirkland", "numéro", "recommandation", "recommande",
    "transcription", "mme", "québec", "mmm", "s.e.n.c") |> 
  setdiff(c("parc", "nature", "energies", "fossiles", "compostage", "marche",
            "organiques", "agriculture", "jardins", "triage", "naturels",
            "fleuri", "corridor", "cooperative")) |> 
  unique()

text_sub <- 
  text_sub |> 
  filter(!word %in% stop_words_mtl)

bigram_sub <- 
  bigram_sub |> 
  filter(!word_1 %in% stop_words_mtl, !word_2 %in% stop_words_mtl)


# Join with result df -----------------------------------------------------

text_sub <- 
  text_sub |> 
  left_join(select(result, id, date, lat, lon, large), by = "id")

bigram_sub <- 
  bigram_sub |> 
  left_join(select(result, id, date, lat, lon, large), by = "id")


# Join with sustainability dictionary -------------------------------------

dict <- 
  read_csv("data/sus_dict_core.csv", show_col_types = FALSE) |> 
  select(word = Mots, green_grey = vert_gris, category = Catégorie) |> 
  filter(!is.na(word), !is.na(category)) |> 
  distinct(word, .keep_all = TRUE)

dict_climate <- 
  read_csv("data/sus_dict_climate.csv", show_col_types = FALSE) |> 
  select(word = Mots, green_grey = vert_gris, category = Catégorie) |> 
  filter(!is.na(word), !is.na(category)) |> 
  mutate(climate = TRUE) |> 
  select(word, climate) |> 
  distinct(word, .keep_all = TRUE)

text_sub <- 
  text_sub |> 
  left_join(dict, by = "word") |> 
  left_join(dict_climate, by = "word") |> 
  mutate(climate = coalesce(climate, FALSE))

bigram_sub <-
  bigram_sub |> 
  left_join(dict, by = c("word_1" = "word")) |> 
  left_join(dict_climate, by = c("word_1" = "word")) |> 
  mutate(climate = coalesce(climate, FALSE)) |> 
  rename(green_grey_1 = green_grey, category_1 = category, 
         climate_1 = climate) |> 
  left_join(dict, by = c("word_2" = "word")) |> 
  left_join(dict_climate, by = c("word_2" = "word")) |> 
  mutate(climate = coalesce(climate, FALSE)) |> 
  rename(green_grey_2 = green_grey, category_2 = category, 
         climate_2 = climate)


# Join with sentiment -----------------------------------------------------

sentiment <- 
  read_delim("data/FEEL.csv", ";", show_col_types = FALSE) |> 
  select(-id)

text_sub <- 
  text_sub |> 
  left_join(select(sentiment, word, polarity), by = "word")

bigram_sub <- 
  bigram_sub |> 
  left_join(select(sentiment, word, polarity), by = c("word_1" = "word")) |> 
  rename(polarity_1 = polarity) |> 
  left_join(select(sentiment, word, polarity), by = c("word_2" = "word")) |> 
  rename(polarity_2 = polarity)


# tf-idf ------------------------------------------------------------------

text_sub_tf <- 
  text_sub |> 
  count(doc_id, word) |> 
  bind_tf_idf(word, doc_id, n)


# Build topic model -------------------------------------------------------

df_sub_sparse <- 
  text_sub |> 
  count(id, doc_id, word, sort = TRUE) |> 
  filter(n >= 100) |> 
  cast_sparse(doc_id, word, n)

topic_model_sub <- stm(df_sub_sparse, K = 50, verbose = FALSE, 
                       init.type = "Spectral")

td_sub_beta <- tidy(topic_model_sub)
td_sub_gamma <- tidy(topic_model_sub, matrix = "gamma", 
                     document_names = rownames(df_sub_sparse))

