# MİLİSİA ( MİLİSLİNUX İLETİŞİM AĞI )
Milis Linux Tox Tabanlı İletişim Ağı 

Milis İşletim Sistemi için p2p toxcore protokolü üzerine kurulmuş iletişim ağı yapı çalışması

Kurulum: (installation)

git clone https://github.com/milisarge/milisia.git

cd milisia

mps -kur toxcore

mps -kur python3-pip

pip3 install aiohttp

./sunucu.sh 

ctrl+c

./sunucu.sh


Debian'dan çalıştırmak için:

https://pkg.tox.chat/debian/pool/jessie/libt/libtoxcore/ adresinden ilgili paketler kurulur.

https://github.com/gjedeer/tuntox/releases  adresinden ilgili tuntox ikilisi milisia dizinine atılır.

./sunucu.sh
