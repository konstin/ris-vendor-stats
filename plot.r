#!/usr/bin/env Rscript

library("ggplot2")
library("reshape2")

theme_set(theme_light())

files <- Sys.glob("results-*.csv")
filenames <- lapply(files, function(filename) {
  sub(".*results-(.*).csv", "\\1", filename)
})

datasets <- lapply(files, function(filename) {
  print(filename)
  df <- read.csv(filename)
  # Remove those not found
  found <- df[df$vendor != "",]
  # found <- found[grepl("105", found$ags),]
  found$vendor <- factor(found$vendor)
  return(found)
})

vendors <- lapply(datasets, function(dataset) {
  table(dataset$vendor)
})

names(vendors) <- filenames

weeks <- melt(vendors, id="rownames")
colnames(weeks) <- c("vendor", "value", "date")
weeks$date <- as.Date(weeks$date)
plot <- ggplot(weeks, aes(x = date, y = value, color = vendor, group = vendor)) + geom_line() + labs(y="Number of Websites")
ggsave("vendors-over-time.svg", plot)
ggsave("vendors-over-time.png", plot)

