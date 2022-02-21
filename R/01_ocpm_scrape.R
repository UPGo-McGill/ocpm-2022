#### OCPM SCRAPE ###############################################################

# Attach packages ---------------------------------------------------------

library(tidyverse)
library(rvest)
library(sf)


# Get list of completed consultations -------------------------------------

home_page <- read_html("https://ocpm.qc.ca/fr/consultations-publiques")

urls <- home_page |> 
  html_element(
    xpath = '//*[@id="node-85"]/div/div/div/div/div[3]/div/div/div[2]/ul') |> 
  html_elements(xpath = 'li') |> 
  html_elements(xpath = 'div') |> 
  html_elements(xpath = 'div') |> 
  html_elements(xpath = 'h1') |> 
  html_elements(xpath = 'a') |> 
  html_attr("href")

urls <- paste0("https://ocpm.qc.ca", urls)


# Construct result data frame ---------------------------------------------

result <- tibble(
  id = seq_along(urls),
  title = NA_character_,
  date = as.Date(NA_character_),
  report = NA,
  sections = vector("list", length(urls)))

# result <- qs::qread("output/result.qs")


# Loop through URLs -------------------------------------------------------

for (i in 1:length(urls)) {
  
  print(paste0(i, ": ", substr(Sys.time(), 12, 16)))
  
  # Get set up
  page <- read_html(urls[i])
  title <- str_remove(urls[i], "https://ocpm.qc.ca/fr/")
  title <- str_remove(title, "consultation-publique/")
  dir.create(paste0("pdf/", i, "_", title))
  result[i,]$title <- title
  
  # Get date
  date <- 
    page |> 
    html_element(xpath = "//*[@class='date-display-single']") |> 
    html_attr("content") |> 
    parse_datetime() |> 
    as.Date()
  result[i,]$date <- date
  
  # Get links
  links <- 
    page |> 
    html_elements(xpath = "//div") |> 
    html_elements(xpath = "a")
  
  # Get report
  result[i,]$report <- tryCatch(suppressWarnings({
    links[html_text(links) == "Lire le rapport"] |> 
      html_attr("href") |> 
      download.file(paste0("pdf/", i, "_", title, "/report.pdf"), quiet = TRUE)
    TRUE
    }), error = function(e) FALSE)
  
  # Check for additional documents
  docs <- 
    urls[i] |> 
    paste0("/documentation") |> 
    read_html()
  
  if ({docs |> 
      html_element(xpath = 'head') |> 
      html_element(xpath = 'title') |> 
      html_text()} == "| OCPM") next

  # Get list of sections  
  result[i,]$sections <- 
    docs |> 
    html_element(xpath = "body") |> 
    html_element(xpath = "div[2]") |> 
    html_element(xpath = "section[2]") |> 
    html_element(xpath = "div[3]") |> 
    html_element(xpath = "div") |> 
    html_element(xpath = "div") |> 
    html_element(xpath = "div") |> 
    html_element(xpath = "div") |> 
    html_text() |> 
    str_remove_all("\n") |> 
    str_squish() |> 
    list()
  
  # Get document URLs
  doc_urls <- 
    docs |> 
    html_elements(xpath = '//*/a') |> 
    html_attr("href") |> 
    str_subset("https://ocpm.qc.ca/sites/ocpm.qc.ca/files/pdf")
  
  # Get destination paths
  dest_paths <-
    doc_urls |> 
    str_remove("https://ocpm.qc.ca/sites/ocpm.qc.ca/files/pdf/") |> 
    str_remove("^.*/")
  dest_paths <- paste0("pdf/", i, "_", title, "/", dest_paths)
  
  # Download files, 50 at a time
  it <- ceiling(length(doc_urls) / 50)
  for (j in seq_along(it)) {
    range <- ((j - 1) * 50 + 1):min(j * 50, length(dest_paths))
    download.file(doc_urls[range], dest_paths[range], quiet = TRUE)
  }
  
  qs::qsave(result, file = "output/result.qs")
  
}


# Add coordinates ---------------------------------------------------------

coordinates <- 
  read_csv("data/coordinates.csv") |> 
  tidyr::separate(Project, c("id", "title"), "_") |> 
  mutate(id = as.integer(id))

coordinates |> 
  anti_join(result, by = "title") |> 
  pull(title)

result <- 
  result |> 
  select(-id) |> 
  inner_join(coordinates, by = "title") |> 
  relocate(id) |> 
  mutate(across(c(Latitude:Longitude), 
                ~as.numeric(if_else(.x == "N/A", NA_character_, .x))),
         Address = if_else(Address == "N/A", NA_character_, Address)) |> 
  rename(lat = Latitude, lon = Longitude, large = `Large project`, 
         address = Address) |> 
  mutate(large = if_else(large == "N/A", NA_character_, large),
         large = if_else(large == 1, TRUE, FALSE))

qs::qsave(result, file = "output/result.qs")


# Save problems for future analysis ---------------------------------------

problems <- warnings()
qs::qsave(problems, file = "output/problems.qs")

