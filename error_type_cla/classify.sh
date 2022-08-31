sed -i "" "s/^Ignored|/__label__Ignored /" all.txt
sed -i "" "s/^NotIgnored|/__label__NotIgnored /" all.txt

cat all.txt | grep NotIgnored > positive.txt
cat all.txt | grep __Ignored > negative.txt

awk 'NR%8!=0' negative.txt > train.txt
awk 'NR%8!=0' positive.txt >> train.txt
# duplicate some positive data
#awk 'NR%8!=0' positive.txt >> train.txt

awk 'NR%8==0' negative.txt > test.txt
awk 'NR%8==0' positive.txt >> test.txt

# duplicate more token datas
#for i in $(seq 1 1); do
#    awk 'NR%8!=0' fb.csv >> train.txt
#done

#awk 'NR%8==0' fb.csv > test.txt

#for i in $(seq 1 20); do
#    awk 'NR%8==0' fb.csv >> test.txt
#done

#awk 'NR%8==0' drain_variables.txt.p.s.l >> test.txt

echo "train"
# fasttext supervised -input train.txt -output error_type_cla -epoch 50 -pretrainedVectors ../model/star.vec  -maxn 3 -minn 1
fasttext supervised -input train.txt -output error_type_cla -epoch 100  -maxn 20 -minn 3 -wordNgrams 10
#fasttext supervised -input train.txt -output error_type_cla -epoch 100  -wordNgrams 5

echo "test"
fasttext test error_type_cla.bin test.txt
fasttext predict error_type_cla.bin test.txt > test.txt.o

