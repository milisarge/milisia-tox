#from settings import Settings
from settings import *
from tox import Tox
from toxcore_enums_and_consts import *
from ctypes import *
#from bot import Bot as Bota
from tox import bin_to_string


def tox_factory(data=None, settings=None):
    """
    :param data: user data from .tox file. None = no saved data, create new profile
    :param settings: current profile settings. None = default settings will be used
    :return: new tox instance
    """
    if settings is None:
        settings = {
            'ipv6_enabled': True,
            'udp_enabled': True,
            'proxy_type': 0,
            'proxy_host': 0,
            'proxy_port': 0,
            'start_port': 0,
            'end_port': 0,
            'tcp_port': 0
        }
    tox_options = Tox.options_new()
    tox_options.contents.udp_enabled = settings['udp_enabled']
    tox_options.contents.proxy_type = settings['proxy_type']
    tox_options.contents.proxy_host = settings['proxy_host']
    tox_options.contents.proxy_port = settings['proxy_port']
    tox_options.contents.start_port = settings['start_port']
    tox_options.contents.end_port = settings['end_port']
    tox_options.contents.tcp_port = settings['tcp_port']
    if data:  # load existing profile
        tox_options.contents.savedata_type = TOX_SAVEDATA_TYPE['TOX_SAVE']
        tox_options.contents.savedata_data = c_char_p(data)
        tox_options.contents.savedata_length = len(data)
    else:  # create new profile
        tox_options.contents.savedata_type = TOX_SAVEDATA_TYPE['NONE']
        tox_options.contents.savedata_data = None
        tox_options.contents.savedata_length = 0
    return Tox(tox_options)


if os.path.isfile("profil.tox"): 
    print ("mevcut profil açılıyor.")
    toxer = tox_factory(ProfileHelper.open_profile("profil.tox"))
else:
    print ("yeni profil açılıyor.")
    toxer= tox_factory(None,None)
    data = toxer.get_savedata()
    ProfileHelper.save_profile(data)


# -----------------------------------------------------------------------------------------------------------------
# Callbacks - current user
# -----------------------------------------------------------------------------------------------------------------

def self_connection_status():
    """
    Current user changed connection status (offline, UDP, TCP)
    """
    def wrapped(tox, connection, user_data):
        print('Baglantı durumu: ', str(connection))
    return wrapped


# -----------------------------------------------------------------------------------------------------------------
# Callbacks - friends
# -----------------------------------------------------------------------------------------------------------------


def friend_connection_status(tox, friend_num, new_status, user_data):
    """
    Check friend's connection status (offline, udp, tcp)
    """
    print("{}. dugum baglandı.Baglantı durumu: {}".format(friend_num, new_status))


def friend_message():
    """
    New message from friend
    """
    def wrapped(tox, friend_number, message_type, message, size, user_data):
        print(message.decode('utf-8'))
        #Bot.get_instance().new_message(friend_number, message.decode('utf-8'))
        #Bota.new_message(Bota,friend_number, message.decode('utf-8'))
        #Bot.new_message(friend_number, message.decode('utf-8'))
        # parse message
    return wrapped


def friend_request(tox,public_key, message, message_size, user_data):
    """
    Called when user get new friend request
    """
    key = ''.join(chr(x) for x in public_key[:TOX_PUBLIC_KEY_SIZE])
    tox_id = bin_to_string(key, TOX_PUBLIC_KEY_SIZE)
    #profile.process_friend_request(tox_id, message.decode('utf-8'))
    print('Dugum baglantı isteği:', message)
    open("yenidugum","w").write(tox_id)
    #toxer.friend_add_norequest(tox_id)
    #data = toxer.get_savedata()
    #ProfileHelper.save_profile(data)


# -----------------------------------------------------------------------------------------------------------------
# Callbacks - file transfers
# -----------------------------------------------------------------------------------------------------------------


def tox_file_recv(tox_link):
    """
    New incoming file
    """
    def wrapped(tox, friend_number, file_number, file_type, size, file_name, file_name_size, user_data):
        ##profile = Bot.get_instance()
        ##profile = Bot()
        if file_type == TOX_FILE_KIND['DATA']:
            print('dosya gonderme istegi geldi',friend_number,"dan")
            file_name = str(file_name[:file_name_size].decode('utf-8'))
            
            
            ##profile.incoming_file_transfer(friend_number, file_number, size, file_name)
        else:  # AVATAR
            tox_link.file_control(friend_number, file_number, TOX_FILE_CONTROL['CANCEL'])
    return wrapped


def file_recv_chunk(tox, friend_number, file_number, position, chunk, length, user_data):
    """
    Incoming chunk
    """
    print ("chunk olayi")
    '''Bot.get_instance().incoming_chunk(
                          friend_number,
                          file_number,
                          position,
                          chunk[:length] if length else None)

    '''
def file_chunk_request(tox, friend_number, file_number, position, size, user_data):
    """
    Outgoing chunk
    """
    print ("chunka olayi")
    '''
    Bot.get_instance().outgoing_chunk(
                          friend_number,
                          file_number,
                          position,
                          size)

    '''
def file_recv_control(tox, friend_number, file_number, file_control, user_data):
    """
    Friend cancelled, paused or resumed file transfer
    """
    if file_control == TOX_FILE_CONTROL['CANCEL']:
        print ("file kontrol")
        ##Bot.get_instance().cancel_transfer(friend_number, file_number, True)

# -----------------------------------------------------------------------------------------------------------------
# Callbacks - initialization
# -----------------------------------------------------------------------------------------------------------------


def init_callbacks(tox):
    print("tox altyapısı başlatıldı.")
    """
    Initialization of all callbacks.
    :param tox: tox instance
    """
    tox.callback_self_connection_status(self_connection_status(), 0)

    tox.callback_friend_message(friend_message(), 0)
    tox.callback_friend_connection_status(friend_connection_status, 0)
    tox.callback_friend_request(friend_request, 0)

    tox.callback_file_recv(tox_file_recv(tox), 0)
    tox.callback_file_recv_chunk(file_recv_chunk, 0)
    tox.callback_file_chunk_request(file_chunk_request, 0)
    tox.callback_file_recv_control(file_recv_control, 0)

