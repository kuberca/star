file=$1
cat $file | fasttext print-sentence-vectors data/star.bin > $file.vec
python sim.py -vector_file $file.vec
cat $file.vec.sim
