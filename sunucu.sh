mkdir -p ozel
mkdir -p paylasim
killall tuntox
if [ ! -f mesaj.log ];then
	touch mesaj.log
fi
if [ "$1" == "-r" ] ; then
	rm -rf ozel/tox_save
	rm -rf profil.tox
	rm *.log
fi

fuser -k 33999/tcp
python3 sunucu.py
