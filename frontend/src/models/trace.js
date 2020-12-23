exports.findLinesWithCode = (code) => {
  let lines = code.split("\n")
  let lineNumbers = []
  lines.forEach((line, idx) => {
    let commentStart = line.indexOf("#")
    if (commentStart < 0) commentStart = line.length
    let cleanLine = line.substring(0, commentStart).trim()
    if (cleanLine.length > 0) lineNumbers.push(idx + 1)
  })
  return lineNumbers
}
