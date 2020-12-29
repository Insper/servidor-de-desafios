exports.traceMessages = t => code => {
  switch (code) {
    case -1:
      return t("An error occurred")
    case 0:
      return ""
    case 1:
      return t("Different than expected")
    case 2:
      return `${t("Difference in whitespaces")}. ${t("There shouldn't be any additional or missing spaces or new lines")}`
    case 3:
      return t("This part of the memory should be inactive")
    case 4:
      return t("This part of the memory should be active")
    case 5:
      return t("Maybe you forgot the quotation marks")
    case 6:
      return t("Wrong return value")
  }
}
