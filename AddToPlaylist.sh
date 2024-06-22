echo "0=$0"
echo "1=$1"
echo "2=$2"
echo "3=$3"
echo "4=$4"
pl=$1/$4.m3u8
echo "pl=$pl"
echo find "$2" -type f -exec file -N -i -- {} + | sed -n 's!: video/[^:]*$!!p'
videofile=$(find "$2" -type f -exec file -N -i -- {} + | sed -n 's!: video/[^:]*$!!p')
echo "videofile=$videofile"
dt=$(date +"%Y-%m-%d %T")
if [ -z "$videofile" ] 
then
	echo "$dt : no video in $2" >> $0.log
else
	echo "$dt : Adding $videofile to $pl" >> $0.log
	echo "#EXTINF:-1,$3">>$pl
	echo $videofile>>$pl
fi

