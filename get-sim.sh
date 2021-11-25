cat all.tpl | fasttext print-sentence-vectors data/star.bin > all.tpl.vec
python sim.py -vector_file all.tpl.vec
