typst compile fancy-docs/zadani.typ fancy-docs/zadani.pdf
pdf2svg fancy-docs/zadani.pdf fancy-docs/zadani.svg
typst compile fancy-docs/main.typ fancy-docs/main.pdf --input type=mp
