#### PRESENTATION FIGURES ######################################################

source("R/00_setup.R")
CT <- qs::qread("output/CT.qs")

province <- 
  cancensus::get_census("CA16", regions = list(PR = "24"), geo_format = "sf") |> 
  st_transform(32618) |> 
  select(geometry)


# Griffintown examples ----------------------------------------------------

text |> 
  filter(id == 5) |> 
  select(id, word)

bigram |> 
  filter(id == 5) |> 
  select(id, word_1, word_2)

text |> 
  filter(id == 5) |> 
  select(id, word, green_grey, category, climate, polarity) |> 
  mutate(green_grey = if_else(green_grey == "gris", "grey", green_grey))


# Topic model example -----------------------------------------------------

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


# Words per report --------------------------------------------------------

# Words per report histogram
words_per_report_hist <-
  text |> 
  count(id) |> 
  ggplot(aes(n)) +
  geom_histogram(fill = "#225EA8") +
  scale_x_continuous(name = NULL, labels = scales::comma) +
  scale_y_continuous(name = NULL, labels = scales::comma) +
  theme_minimal() +
  theme(text = element_text(family = "Futura"),
        plot.background = element_rect(fill = "white", colour = "transparent")) 

ggsave(filename = "output/figures/words_per_report_hist.png", 
       plot = words_per_report_hist, width = 4.5, height = 4, units = "in")

# Words per report scatterplot
words_per_report_long <- 
  text |> 
  count(date, id) |> 
  ggplot(aes(date, n)) +
  geom_point(colour = "#225EA8", size = 0.8, alpha = 0.6) +
  geom_smooth(method = "lm", colour = "#225EA8", se = FALSE) +
  scale_x_date(name = NULL) +
  scale_y_continuous(name = NULL, labels = scales::comma) +
  theme_minimal() +
  theme(text = element_text(family = "Futura"),
        plot.background = element_rect(fill = "white", colour = "transparent")) 
  
ggsave(filename = "output/figures/words_per_report_long.png", 
       plot = words_per_report_long, width = 4.5, height = 4, units = "in")

# Words per consultation histogram
words_per_consultation_hist <-
  text |> 
  count(id) |> 
  mutate(type = "Report") |> 
  bind_rows(
    text_sub |> 
      count(id) |> 
      mutate(type = "Submission")) |> 
  ggplot(aes(n, fill = type, group = type)) +
  geom_histogram() +
  scale_x_continuous(name = NULL, labels = scales::comma) +
  scale_y_continuous(name = NULL, labels = scales::comma) +
  scale_fill_manual(name = NULL, values = c("#225EA8", "#4AA59D")) +
  theme_minimal() +
  theme(text = element_text(family = "Futura"),
        plot.background = element_rect(fill = "white", colour = "transparent"),
        legend.position = "bottom") 

ggsave(filename = "output/figures/words_per_consultation_hist.png", 
       plot = words_per_consultation_hist, width = 4.5, height = 4, units = "in")

# Words per consultation over time
words_per_consultation_long <- 
  text |> 
  count(date, id) |> 
  mutate(type = "Report") |> 
  bind_rows(
    text_sub |> 
      count(date, id) |> 
      mutate(type = "Submission")) |> 
  ggplot(aes(date, n, colour = type)) +
  geom_point(size = 0.8, alpha = 0.6) +
  geom_smooth(method = "lm", se = FALSE) +
  scale_x_date(name = NULL) +
  scale_y_continuous(name = NULL, labels = scales::comma) +
  scale_colour_manual(name = NULL, values = c("#225EA8", "#4AA59D")) +
  theme_minimal() +
  theme(text = element_text(family = "Futura"),
        plot.background = element_rect(fill = "white", colour = "transparent"),
        legend.position = "bottom") 

ggsave(filename = "output/figures/words_per_consultation_long.png", 
       plot = words_per_consultation_long, width = 4.5, height = 4, units = "in")


# Bigrams -----------------------------------------------------------------

bigram |> 
  count(word_1, word_2, sort = TRUE)

bigram_sub |> 
  count(word_1, word_2, sort = TRUE)

bigram |> 
  filter(word_1 %in% dict_climate$word | word_2 %in% dict_climate$word) |> 
  count(word_1, word_2, sort = TRUE)


# Sentiment ---------------------------------------------------------------

# Sentiment histogram
sentiment_hist <-
  text |> 
  group_by(id) |>
  summarize(sentiment = (sum(polarity == "positive", na.rm = TRUE) - 
                           sum(polarity == "negative", na.rm = TRUE)) / n(), 
            .groups = "drop") |> 
  mutate(type = "Report") |> 
  bind_rows(
    text_sub |> 
      group_by(id) |>
      summarize(sentiment = (sum(polarity == "positive", na.rm = TRUE) - 
                               sum(polarity == "negative", na.rm = TRUE)) / n(), 
                .groups = "drop") |> 
      mutate(type = "Submission")) |> 
  ggplot(aes(sentiment, fill = type, group = type)) +
  geom_histogram() +
  scale_x_continuous(name = NULL, labels = scales::percent) +
  scale_y_continuous(name = NULL, labels = scales::comma) +
  scale_fill_manual(name = NULL, values = c("#225EA8", "#4AA59D")) +
  theme_minimal() +
  theme(text = element_text(family = "Futura"),
        plot.background = element_rect(fill = "white", colour = "transparent"),
        legend.position = "bottom") 

ggsave(filename = "output/figures/sentiment_hist.png", 
       plot = sentiment_hist, width = 4.5, height = 4, units = "in")

# Sentiment scatterplot
sentiment_long <-
  text |> 
  group_by(date, id) |>
  summarize(sentiment = (sum(polarity == "positive", na.rm = TRUE) - 
                           sum(polarity == "negative", na.rm = TRUE)) / n(), 
            .groups = "drop") |> 
  mutate(type = "Report") |> 
  bind_rows(
    text_sub |> 
      group_by(date, id) |>
      summarize(sentiment = (sum(polarity == "positive", na.rm = TRUE) - 
                               sum(polarity == "negative", na.rm = TRUE)) / n(), 
                .groups = "drop") |> 
      mutate(type = "Submission")) |> 
  ggplot(aes(date, sentiment, colour = type)) +
  geom_point(size = 0.8, alpha = 0.6) +
  geom_smooth(method = "lm", se = FALSE) +
  scale_x_date(name = NULL) +
  scale_y_continuous(name = NULL, labels = scales::percent) +
  scale_colour_manual(name = NULL, values = c("#225EA8", "#4AA59D")) +
  theme_minimal() +
  theme(text = element_text(family = "Futura"),
        plot.background = element_rect(fill = "white", colour = "transparent"),
        legend.position = "bottom") 

ggsave(filename = "output/figures/sentiment_long.png", 
       plot = sentiment_long, width = 4.5, height = 4, units = "in")


# Sustainability language -------------------------------------------------

# Sustainability language histogram
sus_language_hist <-
  text |> 
  group_by(id) |>
  summarize(sus_pct = sum(!is.na(green_grey)) / n(), .groups = "drop") |> 
  mutate(type = "Report") |> 
  bind_rows(
    text_sub |> 
      group_by(id) |>
      summarize(sus_pct = sum(!is.na(green_grey)) / n(), .groups = "drop") |> 
      mutate(type = "Submission")) |> 
  ggplot(aes(sus_pct, fill = type, group = type)) +
  geom_histogram() +
  scale_x_continuous(name = NULL, labels = scales::percent) +
  scale_y_continuous(name = NULL) +
  scale_fill_manual(name = NULL, values = c("#225EA8", "#4AA59D")) +
  theme_minimal() +
  theme(text = element_text(family = "Futura"),
        plot.background = element_rect(fill = "white", colour = "transparent"),
        legend.position = "bottom") 

ggsave(filename = "output/figures/sus_language_hist.png", 
       plot = sus_language_hist, width = 4.5, height = 4, units = "in")

# Sustainability language scatterplot
sus_language_long <-
  text |> 
  group_by(date, id) |>
  summarize(sus_pct = sum(!is.na(green_grey)) / n(), .groups = "drop") |> 
  mutate(type = "Report") |> 
  bind_rows(
    text_sub |> 
      group_by(date, id) |>
      summarize(sus_pct = sum(!is.na(green_grey)) / n(), .groups = "drop") |> 
      mutate(type = "Submission")) |> 
  ggplot(aes(date, sus_pct, colour = type)) +
  geom_point(size = 0.8, alpha = 0.6) +
  geom_smooth(method = "lm", se = FALSE) +
  scale_x_date(name = NULL) +
  scale_y_continuous(name = NULL, labels = scales::percent) +
  scale_colour_manual(name = NULL, values = c("#225EA8", "#4AA59D")) +
  theme_minimal() +
  theme(text = element_text(family = "Futura"),
        plot.background = element_rect(fill = "white", colour = "transparent"),
        legend.position = "bottom") 

ggsave(filename = "output/figures/sus_language_long.png", 
       plot = sus_language_long, width = 4.5, height = 4, units = "in")


# Climate language --------------------------------------------------------

# Climate language histogram
climate_language_hist <-
  text |> 
  group_by(id) |>
  summarize(clim_pct = mean(climate), .groups = "drop") |> 
  mutate(type = "Report") |> 
  bind_rows(
    text_sub |> 
      group_by(id) |>
      summarize(clim_pct = mean(climate), .groups = "drop") |> 
      mutate(type = "Submission")) |> 
  ggplot(aes(clim_pct, fill = type, group = type)) +
  geom_histogram() +
  scale_x_continuous(name = NULL, labels = scales::percent,
                     limits = c(0, 0.005)) +
  scale_y_continuous(name = NULL) +
  scale_fill_manual(name = NULL, values = c("#225EA8", "#4AA59D")) +
  theme_minimal() +
  theme(text = element_text(family = "Futura"),
        plot.background = element_rect(fill = "white", colour = "transparent"),
        legend.position = "bottom") 

ggsave(filename = "output/figures/climate_language_hist.png", 
       plot = climate_language_hist, width = 4.5, height = 4, units = "in")

# Climate language scatterplot
climate_language_long <-
  text |> 
  group_by(date, id) |>
  summarize(clim_pct = mean(climate), .groups = "drop") |> 
  mutate(type = "Report") |> 
  bind_rows(
    text_sub |> 
      group_by(date, id) |>
      summarize(clim_pct = mean(climate), .groups = "drop") |> 
      mutate(type = "Submission")) |> 
  ggplot(aes(date, clim_pct, colour = type)) +
  geom_point(size = 0.8, alpha = 0.6) +
  geom_smooth(method = "lm", se = FALSE) +
  scale_x_date(name = NULL) +
  scale_y_continuous(name = NULL, labels = scales::percent, limits = c(0, 0.005)) +
  scale_colour_manual(name = NULL, values = c("#225EA8", "#4AA59D")) +
  theme_minimal() +
  theme(text = element_text(family = "Futura"),
        plot.background = element_rect(fill = "white", colour = "transparent"),
        legend.position = "bottom") 

ggsave(filename = "output/figures/climate_language_long.png", 
       plot = climate_language, width = 4.5, height = 4, units = "in")


# Climate versus sustainability -------------------------------------------

# Climate versus sustainability
clim_v_sus <- 
  text |> 
  group_by(date, id) |>
  summarize(sus_pct = sum(!is.na(green_grey)) / n(),
            clim_pct = mean(climate), .groups = "drop") |> 
  mutate(type = "Report") |> 
  bind_rows(
    text_sub |> 
      group_by(date, id) |>
      summarize(sus_pct = sum(!is.na(green_grey)) / n(),
                clim_pct = mean(climate), .groups = "drop") |> 
      mutate(type = "Submission")) |> 
  mutate(ratio = clim_pct / sus_pct) |> 
  group_by(date, id) |> 
  summarize(rat_dif = ratio[type == "Report"] - ratio[type == "Submission"],
            .groups = "drop") |> 
  ggplot(aes(date, rat_dif, colour = rat_dif >= 0)) +
  geom_point(size = 0.8) +
  scale_x_date(name = NULL) +
  scale_y_continuous(name = NULL) +
  scale_colour_manual(name = NULL, 
                      labels = c("Submissions more climate-focused",
                                 "Report more climate-focused"),
                      values = c("#225EA8", "#4AA59D")) +
  theme_minimal() +
  theme(text = element_text(family = "Futura"),
        plot.background = element_rect(fill = "white", colour = "transparent"),
        legend.position = "bottom") 

ggsave(filename = "output/figures/clim_v_sus.png", 
       plot = clim_v_sus, width = 5, height = 4, units = "in")


# Map of climate language -------------------------------------------------

climate_language_map <-
  text |> 
  group_by(date, id, lat, lon) |>
  summarize(clim_pct = mean(climate), .groups = "drop") |> 
  mutate(type = "Report") |> 
  bind_rows(
    text_sub |> 
      group_by(date, id, lat, lon) |>
      summarize(clim_pct = mean(climate), .groups = "drop") |> 
      mutate(type = "Submission")) |> 
  filter(!is.na(lat), !is.na(lon)) |> 
  st_as_sf(coords = c("lon", "lat"), crs = 4326) |> 
  ggplot() +
  geom_sf(data = province, colour = "transparent", fill = "grey93") +
  geom_sf(data = CT, colour = "transparent", fill = "grey80") +
  geom_sf(aes(colour = type, size = clim_pct), alpha = 0.5) +
  scale_colour_manual(name = "Type", values = c("#225EA8", "#4AA59D")) +
  scale_size(name = "% climate words", labels = scales::percent) +
  upgo::gg_bbox(CT) +
  theme_void() +
  theme(text = element_text(family = "Futura"),
        plot.background = element_rect(fill = "white", colour = "transparent"),
        legend.position = "right") 

ggsave(filename = "output/figures/climate_language_map.png", 
       plot = climate_language_map, width = 6, height = 4, units = "in")



# Census analysis ---------------------------------------------------------

# Income scatterplot
income_scatter <- 
  text |> 
  group_by(date, id, lat, lon, large) |>
  summarize(clim_pct = mean(climate), .groups = "drop") |> 
  mutate(type = "Report") |> 
  bind_rows(
    text_sub |> 
      group_by(date, id, lat, lon, large) |>
      summarize(clim_pct = mean(climate), .groups = "drop") |> 
      mutate(type = "Submission")) |> 
  filter(!is.na(lat), !is.na(lon)) |> 
  st_as_sf(coords = c("lon", "lat"), crs = 4326) |> 
  filter(!large, clim_pct > 0) |> 
  st_join(CT) |> 
  ggplot(aes(med_income, clim_pct, colour = type)) +
  geom_point(size = 0.8, alpha = 0.6) +
  geom_smooth(method = "lm", se = FALSE) +
  scale_x_continuous(name = "Median HH income", labels = scales::dollar, 
                     limits = c(15000, 100000)) +
  scale_y_continuous(name = "Climate words", labels = scales::percent, 
                     limits = c(0, 0.005)) +
  scale_colour_manual(name = NULL, values = c("#225EA8", "#4AA59D")) +
  theme_minimal() +
  theme(text = element_text(family = "Futura"),
        plot.background = element_rect(fill = "white", colour = "transparent"),
        legend.position = "bottom") 

ggsave(filename = "output/figures/income_scatter.png", 
       plot = income_scatter, width = 4.5, height = 4, units = "in")

# Visible minority scatterplot
vis_min_scatter <- 
  text |> 
  group_by(date, id, lat, lon, large) |>
  summarize(clim_pct = mean(climate), .groups = "drop") |> 
  mutate(type = "Report") |> 
  bind_rows(
    text_sub |> 
      group_by(date, id, lat, lon, large) |>
      summarize(clim_pct = mean(climate), .groups = "drop") |> 
      mutate(type = "Submission")) |> 
  filter(!is.na(lat), !is.na(lon)) |> 
  st_as_sf(coords = c("lon", "lat"), crs = 4326) |> 
  filter(!large, clim_pct > 0) |> 
  st_join(CT) |> 
  ggplot(aes(vis_min, clim_pct, colour = type)) +
  geom_point(size = 0.8, alpha = 0.6) +
  geom_smooth(method = "lm", se = FALSE) +
  scale_x_continuous(name = "Visible minorities", labels = scales::percent) +
  scale_y_continuous(name = "Climate words", labels = scales::percent, 
                     limits = c(0, 0.005)) +
  scale_colour_manual(name = NULL, values = c("#225EA8", "#4AA59D")) +
  theme_minimal() +
  theme(text = element_text(family = "Futura"),
        plot.background = element_rect(fill = "white", colour = "transparent"),
        legend.position = "bottom") 

ggsave(filename = "output/figures/vis_min_scatter.png", 
       plot = vis_min_scatter, width = 4.5, height = 4, units = "in")


# Topic models ------------------------------------------------------------

top_terms <- 
  td_beta |>  
  arrange(beta) |> 
  group_by(topic) |> 
  top_n(7, beta) |> 
  arrange(-beta) |> 
  select(topic, term) |> 
  summarise(terms = list(term)) |> 
  mutate(terms = map(terms, paste, collapse = ", ")) |> 
  unnest(terms)

top_100_terms <-
  td_beta |>  
  group_by(topic) |> 
  slice_max(beta, n = 100) |> 
  ungroup()

gamma_terms <- 
  td_gamma |> 
  group_by(topic) |> 
  summarise(gamma = mean(gamma)) |> 
  arrange(desc(gamma)) |> 
  left_join(top_terms, by = "topic") |> 
  mutate(topic = paste0("Topic ", topic),
         topic = reorder(topic, gamma))

# Top 20 topics
topic_graph <- 
  gamma_terms |> 
  top_n(20, gamma) |> 
  ggplot(aes(topic, gamma, label = terms, fill = topic)) +
  geom_col(show.legend = FALSE) +
  geom_text(hjust = 0, nudge_y = 0.0005, size = 3, family = "Futura") +
  coord_flip() +
  scale_y_continuous(expand = c(0,0),
                     limits = c(0, 0.2),
                     labels = scales::percent_format()) +
  scale_fill_manual(values = c("#771155", "#AA4488", "#CC99BB", "#114477", 
                               "#4477AA", "#77AADD", "#117777", "#44AAAA", 
                               "#77CCCC", "#117744", "#44AA77", "#88CCAA", 
                               "#777711", "#AAAA44", "#DDDD77", "#774411", 
                               "#AA7744", "#DDAA77", "#771122", "#AA4455")) +
  theme_tufte(ticks = FALSE, base_family = "Futura") +
  theme(text = element_text(family = "Futura")) +
  labs(x = NULL, y = expression(gamma))

ggsave(filename = "output/figures/topic_graph.png", 
       plot = topic_graph, width = 8, height = 4, units = "in")

# Sustainability topics
top_20_sus_topics <- 
  top_100_terms |> 
  semi_join(dict, by = c("term" = "word")) |> 
  filter(beta != 1) |> 
  group_by(topic) |> 
  summarize(beta = sum(beta)) |> 
  arrange(-beta) |> 
  slice(1:20)

# Top 20 topics
topic_sus_graph <- 
  td_gamma |> 
  group_by(topic) |> 
  summarise(gamma = mean(gamma)) |> 
  inner_join(top_20_sus_topics) |> 
  arrange(desc(beta)) |> 
  left_join(top_terms, by = "topic") |> 
  mutate(topic = paste0("Topic ", topic),
         topic = reorder(topic, gamma)) |> 
  ggplot(aes(topic, gamma, label = terms, fill = topic)) +
  geom_col(show.legend = FALSE) +
  geom_text(hjust = 0, nudge_y = 0.0005, size = 3, family = "Futura") +
  coord_flip() +
  scale_y_continuous(expand = c(0,0),
                     limits = c(0, 0.2),
                     labels = scales::percent_format()) +
  scale_fill_manual(values = c("#771155", "#AA4488", "#CC99BB", "#114477", 
                               "#4477AA", "#77AADD", "#117777", "#44AAAA", 
                               "#77CCCC", "#117744", "#44AA77", "#88CCAA", 
                               "#777711", "#AAAA44", "#DDDD77", "#774411", 
                               "#AA7744", "#DDAA77", "#771122", "#AA4455")) +
  theme_tufte(ticks = FALSE, base_family = "Futura") +
  theme(text = element_text(family = "Futura")) +
  labs(x = NULL, y = expression(gamma))

ggsave(filename = "output/figures/topic_sus_graph.png", 
       plot = topic_sus_graph, width = 8, height = 4, units = "in")

# Which reports have most coverage from sustainability topics
top_100_terms |> 
  semi_join(dict, by = c("term" = "word")) |> 
  filter(beta != 1) |> 
  group_by(topic) |> 
  summarize(beta = sum(beta)) |> 
  full_join(td_gamma) |> 
  group_by(document) |> 
  summarize(sus_weight = sum(beta * gamma)) |> 
  arrange(-sus_weight)


