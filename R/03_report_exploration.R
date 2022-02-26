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

reports <-
  list.files(path = "pdf", pattern = "pdf", recursive = TRUE, 
             full.names = TRUE) |> 
  str_subset("/report.pdf$")
  
text_raw <- 
  map_dfr(reports, ~{
  tibble(id = str_extract(.x, "^pdf/[:digit:]*_") |> 
           str_remove("^pdf/") |> 
           str_remove("_$") |> 
           as.integer(),
         text =  list(pdftools::pdf_text(.x)))}) |> 
  unnest(text)


# Tokenize texts ----------------------------------------------------------

text <- 
  text_raw |> 
  unnest_tokens(word, text) |> 
  mutate(word = if_else(str_detect(word, "’|'|‘"), 
                        str_extract(word, ".+(?=(’|'|‘))"), word)) |> 
  filter(!str_detect(word, "\\d")) |> 
  filter(!str_detect(word, "\\.com|\\.ca")) |> 
  filter(str_detect(word, "[:alpha:]"))

bigram <- 
  text_raw |> 
  unnest_tokens(word, text, token = "ngrams", n = 2) |>  
  filter(!is.na(word)) |> 
  separate(word, c("word_1", "word_2"), sep = " ") |> 
  filter(!str_detect(word_1, "\\d"), !str_detect(word_2, "\\d")) |> 
  filter(!str_detect(word_1, "\\.com|\\.ca"), 
         !str_detect(word_2, "\\.com|\\.ca")) |> 
  filter(str_detect(word_1, "[:alpha:]"), str_detect(word_2, "[:alpha:]"))


# Detect language and only keep French ------------------------------------

langs <- 
  text |> 
  group_by(id) |> 
  summarize(word = paste(word, collapse = " ")) |> 
  mutate(lang = textcat(word))

text <- 
  text |> 
  filter(id %in% which(langs$lang == "french"))

bigram <- 
  bigram |> 
  filter(id %in% which(langs$lang == "french"))


# Remove stop words -------------------------------------------------------

text <- 
  text |> 
  anti_join(stop_words_fr, by = "word")

bigram <- 
  bigram |> 
  anti_join(stop_words_fr, by = c("word_1" = "word")) |> 
  anti_join(stop_words_fr, by = c("word_2" = "word"))

stop_words_mtl <- 
  result |> 
  pull(title) |> 
  str_split("-") |> 
  unlist() |> 
  unique() |> 
  c(text |> 
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

text <- 
  text |> 
  filter(!word %in% stop_words_mtl)

bigram <- 
  bigram |> 
  filter(!word_1 %in% stop_words_mtl, !word_2 %in% stop_words_mtl)


# Join with result df -----------------------------------------------------

text <- 
  text |> 
  left_join(select(result, id, date, lat, lon, large), by = "id")

bigram <- 
  bigram |> 
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

text <- 
  text |> 
  left_join(dict, by = "word") |> 
  left_join(dict_climate, by = "word") |> 
  mutate(climate = coalesce(climate, FALSE))
  
bigram <-
  bigram |> 
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

text <- 
  text |> 
  left_join(select(sentiment, word, polarity), by = "word")

bigram <- 
  bigram |> 
  left_join(select(sentiment, word, polarity), by = c("word_1" = "word")) |> 
  rename(polarity_1 = polarity) |> 
  left_join(select(sentiment, word, polarity), by = c("word_2" = "word")) |> 
  rename(polarity_2 = polarity)


# tf-idf ------------------------------------------------------------------

text_tf <- 
  text |> 
  count(id, word) |> 
  bind_tf_idf(word, id, n)


# Build topic model -------------------------------------------------------

df_sparse <- 
  text |> 
  count(id, word, sort = TRUE) |> 
  filter(n >= 100) |> 
  cast_sparse(id, word, n)

topic_model <- stm(df_sparse, K = 50, verbose = FALSE, init.type = "Spectral")

td_beta <- tidy(topic_model)
td_gamma <- tidy(topic_model, matrix = "gamma", 
                 document_names = rownames(df_sparse))
