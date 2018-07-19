#!/bin/bash

for i in fig/*.svg;do
    outfn=${i#fig/}
    outfn=${outfn%.svg}.pdf
    inkscape --export-area-drawing --export-pdf=renders/$outfn $i
done


for i in fig/*.py;do
    python $i
done