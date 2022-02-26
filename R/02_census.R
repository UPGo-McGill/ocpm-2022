#### GET CENSUS DATA ###########################################################

source("R/00_setup.R")
library(cancensus)


# Get CT-level data -------------------------------------------------------

CT <- 
  cancensus::get_census("CA16", list(CSD = "2466023"), level = "CT",
                        vectors = c("med_income" = "v_CA16_2398",
                                    "tot_min" = "v_CA16_3954",
                                    "vis_min" = "v_CA16_3957",
                                    "tot_imm" = "v_CA16_3405",
                                    "imm" = "v_CA16_3411"),
                        geo_format = "sf") |> 
  mutate(vis_min = vis_min / tot_min, imm = imm / tot_imm) |> 
  select(GeoUID, population = Population, med_income, vis_min, imm)

qs::qsave(CT, "output/CT.qs")
