MEDIA_PATH=$(cd `dirname $0`'/media' && pwd)
LESS_FILES_PATH=$MEDIA_PATH'/less_src'
CSS_OUTPUT_PATH=$MEDIA_PATH'/css' 

if [ ! -d $CSS_OUTPUT_PATH ]
then
	mkdir $CSS_OUTPUT_PATH
fi
cp -R $LESS_FILES_PATH/* $CSS_OUTPUT_PATH

for file in `find "$LESS_FILES_PATH" -name '*.less' -type f -maxdepth 2`
do
	rel_path=`python -c "import os.path; print os.path.relpath(\"$file\", \"$LESS_FILES_PATH\")"`
	dest_path=$CSS_OUTPUT_PATH'/'$rel_path
	rm $dest_path
	if [ ! -d `dirname $dest_path` ]
	then
		mkdir `dirname $dest_path`
	fi
	echo "generating css file ${dest_path%.less}.css"
	lessc $file > ${dest_path%.less}'.css'
done
