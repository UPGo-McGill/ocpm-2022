#### OCPM REPORT ANALYSIS ######################################################

source("R/00_setup.R")
library(pdftools)
library(tidytext)
library(stm)
# library(tesseract)
# library(quanteda)
library(ggthemes)
library(furrr)
plan(multisession)


# Convert PDF to TXT ------------------------------------------------------

reports <-
  list.files(path = "pdf", pattern = "pdf", recursive = TRUE, 
             full.names = TRUE) |> 
  str_subset("report.pdf$")
  
text_list <- 
  map_dfr(reports, ~{
  tibble(project = str_extract(.x, "^pdf/[:digit:]*_") |> 
           str_remove("^pdf/") |> 
           str_remove("_$"),
         text =  list(pdftools::pdf_text(.x)))}) |> 
  unnest(text)


# Tokenize texts ----------------------------------------------------------

tidy_text_list <- 
  text_list |> 
  unnest_tokens(word, text) |> 
  mutate(word = if_else(str_detect(word, "’|'|‘"), 
                        str_extract(word, ".+(?=(’|'|‘))"), word)) |> 
  anti_join(stop_words_fr) |> 
  filter(!str_detect(word, "\\d")) |> 
  filter(!str_detect(word, ".com"))


# Remove Montreal/OCPM words ----------------------------------------------

stop_words_mtl <- 
  result |> 
  pull(title) |> 
  str_split("-") |> 
  unlist() |> 
  unique() |> 
  c("doc", "montréal", "ville", "consultation", "publique", "office", "projet",
    "grâce", "côte", "hubert", "villeray", "rené", "lévesque", "hochelaga",
    "mercier")

tidy_text_list <- 
  tidy_text_list |> 
  filter(!word %in% stop_words_mtl)

# Join with sustainability dictionary -------------------------------------

dict <- 
  read_csv("data/sus_dictionary.csv") |> 
  select(word = Mots, green_grey = vert_gris, category = Catégorie) |> 
  filter(!is.na(word), !is.na(category))

word_pct <- 
  tidy_text_list |> 
  group_by(project) |> 
  summarize(
    total = n(),
    sus_words = sum(word %in% dict$word),
    green_words = sum(word %in% dict[dict$green_grey == "vert",]$word),
    grey_words = sum(word %in% dict[dict$green_grey == "gris",]$word),
    sus_pct = sus_words / total,
    green_pct = green_words / total,
    grey_pct = grey_words / total) |> 
  mutate(project = as.integer(project))


# Join with result df -----------------------------------------------------

result_word <- 
  result |> 
  inner_join(word_pct, by = c("id" = "project"))

result_cat <-
  tidy_text_list |> 
  group_by(project) |> 
  summarize(total = n()) |> 
  bind_cols({
    map_dfc(unique(dict$category), ~{
      tidy_text_list |> 
        group_by(project) |> 
        summarize(tot = sum(word %in% dict[dict$category == .x,]$word)) |> 
        select(-project) |> 
        set_names(.x)})
    }) |> 
  pivot_longer(cols = -c(project)) |> 
  mutate(project = as.integer(project))

result_cat <- 
  result |> 
  inner_join(result_cat, by = c("id" = "project"))


# Exploratory visualizations ----------------------------------------------

# Number of words over time
result_word |> 
  ggplot(aes(date, total)) +
  geom_point() +
  geom_smooth(method = "lm") +
  theme_minimal()

# Sustainability words over time
result_word |> 
  # filter(date >= "2005-01-01") |> 
  ggplot(aes(date, sus_pct)) +
  geom_point() +
  geom_smooth(method = "lm") +
  theme_minimal()

# Green words over time
result_word |> 
  # filter(date >= "2005-01-01") |> 
  ggplot(aes(date, green_pct)) +
  geom_point() +
  geom_smooth(method = "lm") +
  theme_minimal()

# Grey words over time
result_word |> 
  # filter(date >= "2005-01-01") |> 
  ggplot(aes(date, grey_pct)) +
  geom_point() +
  geom_smooth(method = "lm") +
  theme_minimal()

# Category words over time
result_cat |> 
  group_by(id) |> 
  mutate(value = value / value[name == "total"]) |> 
  ungroup() |> 
  filter(name != "total") |> 
  ggplot(aes(date, value, colour = name)) +
  # geom_point() +
  geom_smooth(method = "lm") +
  facet_wrap(vars(name)) +
  theme_minimal()

result_word |> 
  select(date, sus_pct) |>
  # filter(date >= "2005-01-01") |> 
  transmute(year = lubridate::year(date), sus_pct) |> 
  na.omit() |> 
  cor()



### Exploratory visualizations #################################################

# tf_idf <-
#   tidy_text_list |> 
#   count(project, word, sort = TRUE) |> 
#   bind_tf_idf(word, project, n) |> 
#   arrange(-tf_idf) |> 
#   group_by(project) |> 
#   top_n(10) |> 
#   ungroup()
# 
# figure_1 <-
#   tf_idf %>%
#   filter(city %in% c("Palm Springs", "Santa Cruz", "Colma", "Berkeley", 
#                      "Duarte", "Redwood City")) %>% 
#   mutate(word = reorder_within(word, tf_idf, city)) %>%
#   ggplot(aes(word, tf_idf, fill = city)) +
#   geom_col(alpha = 0.8, show.legend = FALSE) +
#   facet_wrap(~ city, scales = "free", ncol = 3) +
#   scale_fill_brewer(palette = "Set2") +
#   scale_x_reordered() +
#   coord_flip() +
#   theme_minimal() +
#   theme(strip.text=element_text(size=11),
#         text = element_text(family = "Futura"),
#         plot.title = element_text(family = "Futura", face = "bold", 
#                                   hjust = 0.5)) +
#   labs(x = NULL, y = "tf-idf",
#        title = "Highest tf-idf words in climate action plans")
# 
# ggsave("output/figure_1.pdf", plot = figure_1, width = 10, height = 5, 
#        units = "in", useDingbats = FALSE)
  


### Topic model ################################################################

dfm <- 
  tidy_text_list |> 
  count(project, word, sort = TRUE) |> 
  cast_dfm(project, word, n)

df_sparse <- 
  tidy_text_list |> 
  count(project, word, sort = TRUE) |> 
  cast_sparse(project, word, n)

topic_model <- stm(dfm, K = 6, verbose = FALSE, init.type = "Spectral")
td_beta <- tidy(topic_model)
td_gamma <- tidy(topic_model, matrix = "gamma", document_names = rownames(dfm))



### Topic model visualizations #################################################

# figure_2 <- 
  td_beta %>%
  group_by(topic) %>%
  top_n(10, beta) %>%
  ungroup() %>%
  mutate(topic = paste0("Topic ", topic),
         term = reorder_within(term, beta, topic)) %>%
  ggplot(aes(term, beta, fill = as.factor(topic))) +
  geom_col(alpha = 0.8, show.legend = FALSE) +
  facet_wrap(~ topic, scales = "free_y") +
  scale_fill_brewer(palette = "Set2") +
  coord_flip() +
  scale_x_reordered() +
  theme_minimal() +
  labs(x = NULL, y = expression(beta),
       title = "Highest word probabilities for each topic")

# ggsave("output/figure_2.pdf", plot = figure_2, width = 10, height = 5, 
#        units = "in", useDingbats = FALSE)


# figure_3 <- 
  td_gamma %>% 
  ggplot(aes(gamma, fill = as.factor(topic))) +
  geom_histogram(alpha = 0.8, show.legend = FALSE) +
  facet_wrap(~ topic, ncol = 3) +
  scale_fill_brewer(palette = "Set2") +
  labs(title = "Distribution of document probabilities for each topic",
       y = "Number of plans", x = expression(gamma)) +
  theme_minimal() +
  theme(text = element_text(family = "Futura"),
        plot.title = element_text(family = "Futura", face = "bold", 
                                  hjust = 0.5))

# ggsave("output/figure_3.pdf", plot = figure_3, width = 10, height = 5, 
#        units = "in", useDingbats = FALSE)


### Many models ################################################################

df_sparse <- 
  tidy_text_list %>% 
  add_count(word) %>% 
  filter(n > 100) %>% 
  select(-n) %>% 
  count(project, word) %>%
  cast_sparse(project, word, n)

many_models <- 
  tibble(K = c(10, 20, 40, 50, 60, 70, 80, 100, 120)) %>%
  mutate(topic_model = future_map(K, ~stm(df_sparse, K = ., verbose = FALSE)))


### Diagnostics ################################################################

heldout <- make.heldout(df_sparse)

k_result <- 
  many_models %>%
  mutate(exclusivity = map(topic_model, exclusivity),
         semantic_coherence = map(topic_model, semanticCoherence, df_sparse),
         eval_heldout = map(topic_model, eval.heldout, heldout$missing),
         residual = map(topic_model, checkResiduals, df_sparse),
         bound =  map_dbl(topic_model, function(x) max(x$convergence$bound)),
         lfact = map_dbl(topic_model, function(x) lfactorial(x$settings$dim$K)),
         lbound = bound + lfact,
         iterations = map_dbl(topic_model, 
                              function(x) length(x$convergence$bound)))

figure_4 <- 
  k_result %>%
  transmute(K,
            `Lower bound` = lbound,
            Residuals = map_dbl(residual, "dispersion"),
            `Semantic coherence` = map_dbl(semantic_coherence, mean),
            `Held-out likelihood` = map_dbl(eval_heldout, "expected.heldout")) %>%
  gather(Metric, Value, -K) %>%
  ggplot(aes(K, Value, color = Metric)) +
  geom_line(size = 1.5, alpha = 0.7, show.legend = FALSE) +
  facet_wrap(~Metric, scales = "free_y") +
  scale_colour_brewer(palette = "Set2") +
  labs(x = "K (number of topics)",
       y = NULL,
       title = "Model diagnostics by number of topics") +
  theme_minimal() +
  theme(text = element_text(family = "Futura"),
        plot.title = element_text(family = "Futura", face = "bold", 
                                  hjust = 0.5))

# ggsave("output/figure_4.pdf", plot = figure_4, width = 10, height = 5, 
#        units = "in", useDingbats = FALSE)


### Final topic model ##########################################################

topic_model <- k_result %>% 
  filter(K == 70) %>% 
  pull(topic_model) %>% 
  .[[1]]

td_beta <- tidy(topic_model)
td_gamma <- tidy(topic_model, matrix = "gamma",
                 document_names = rownames(df_sparse))





### Graph of top 20 topics #####################################################

top_terms <- 
  td_beta %>%
  arrange(beta) %>%
  group_by(topic) %>%
  top_n(7, beta) %>%
  arrange(-beta) %>%
  select(topic, term) %>%
  summarise(terms = list(term)) %>%
  mutate(terms = map(terms, paste, collapse = ", ")) %>% 
  unnest()

gamma_terms <- 
  td_gamma %>%
  group_by(topic) %>%
  summarise(gamma = mean(gamma)) %>%
  arrange(desc(gamma)) %>%
  left_join(top_terms, by = "topic") %>%
  mutate(topic = paste0("Topic ", topic),
         topic = reorder(topic, gamma))

# figure_5 <- 
  gamma_terms %>%
  top_n(20, gamma) %>%
  ggplot(aes(topic, gamma, label = terms, fill = topic)) +
  geom_col(show.legend = FALSE) +
  geom_text(hjust = 0, nudge_y = 0.0005, size = 3, family = "Futura") +
  coord_flip() +
  scale_y_continuous(expand = c(0,0),
                     limits = c(0, 0.09),
                     labels = scales::percent_format()) +
  scale_fill_manual(values = c("#771155", "#AA4488", "#CC99BB", "#114477", 
                               "#4477AA", "#77AADD", "#117777", "#44AAAA", 
                               "#77CCCC", "#117744", "#44AA77", "#88CCAA", 
                               "#777711", "#AAAA44", "#DDDD77", "#774411", 
                               "#AA7744", "#DDAA77", "#771122", "#AA4455")) +
  theme_tufte(ticks = FALSE, base_family = "Futura") +
  theme(text = element_text(family = "Futura"),
        plot.title = element_text(family = "Futura", face = "bold", 
                                  hjust = 0.5)) +
  labs(x = NULL, y = expression(gamma),
       title = "Top 20 topics in the OCPM report corpus")

# ggsave("output/figure_5.pdf", plot = figure_5, width = 10, height = 5, 
#        units = "in", useDingbats = FALSE)


