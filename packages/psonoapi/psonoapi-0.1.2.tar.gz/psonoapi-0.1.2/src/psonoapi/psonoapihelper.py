import requests
import json
import nacl.encoding
import nacl.signing
import nacl.secret
import binascii
import uuid
import logging
from nacl.public import PrivateKey, PublicKey, Box
from .datamodels import *
from .exceptions import *


class PsonoAPIHelper:
    logger = logging.getLogger(__name__)
    @staticmethod
    def generate_client_login_info(session: PsonoServerSession):
        """
        Generates and signs the login info
        Returns a tuple of the session private key and the login info
        """

        box = PrivateKey.generate()
        session.private_key = box.encode(encoder=nacl.encoding.HexEncoder).decode()
        session.public_key = box.public_key.encode(encoder=nacl.encoding.HexEncoder).decode()

        info = {
            'api_key_id': session.server.key_id,
            'session_public_key': session.public_key,
            'device_description': session.server.session_name,
        }

        info = json.dumps(info)

        signing_box = nacl.signing.SigningKey(session.server.private_key, encoder=nacl.encoding.HexEncoder)

        # The first 128 chars (512 bits or 64 bytes) are the actual signature, the rest the binary encoded info
        signed = signing_box.sign(info.encode())
        signature = binascii.hexlify(signed.signature)

        return  {
            'info': info,
            'signature': signature.decode(),
        }
    @staticmethod
    def decrypt_server_login_info(login_info_hex, login_info_nonce_hex, session: PsonoServerSession):
        """
        Takes the login info and nonce together with the session public and private key.
        Will decrypt the login info and interpret it as json and return the json parsed object.
        """

        crypto_box = Box(PrivateKey(session.private_key, encoder=nacl.encoding.HexEncoder),
                        PublicKey(session.public_key, encoder=nacl.encoding.HexEncoder))

        login_info = nacl.encoding.HexEncoder.decode(login_info_hex)
        login_info_nonce = nacl.encoding.HexEncoder.decode(login_info_nonce_hex)

        login_info = json.loads(crypto_box.decrypt(login_info, login_info_nonce).decode())

        return login_info
    
    @staticmethod
    def verify_signature(login_info, login_info_signature,server_signature):
        """
        Takes the login info and the provided signature and will validate it with the help of server_signature.

        Will raise an exception if it does not match.
        """

        verify_key = nacl.signing.VerifyKey(server_signature, encoder=nacl.encoding.HexEncoder)

        verify_key.verify(login_info.encode(), binascii.unhexlify(login_info_signature))

    @staticmethod
    def encrypt_symmetric(msg, secret):
        """
        Encrypts a message with a random nonce and a given secret
        """

        # generate random nonce
        nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)

        # open crypto box with session secret
        secret_box = nacl.secret.SecretBox(secret, encoder=nacl.encoding.HexEncoder)

        # encrypt msg with crypto box and nonce
        encrypted = secret_box.encrypt(msg.encode(), nonce)

        # cut away the nonce
        text = encrypted[len(nonce):]

        # convert nonce and encrypted msg to hex
        nonce_hex = nacl.encoding.HexEncoder.encode(nonce).decode()
        text_hex = nacl.encoding.HexEncoder.encode(text).decode()
        return {'text': text_hex, 'nonce': nonce_hex}


    @staticmethod
    def decrypt_symmetric(text_hex, nonce_hex, secret):
        """
        Decryts an encrypted text with nonce with the given secret

        :param text_hex:
        :type text_hex:
        :param nonce_hex:
        :type nonce_hex:
        :param secret:
        :type secret:
        :return:
        :rtype:
        """

        text = nacl.encoding.HexEncoder.decode(text_hex)
        nonce = nacl.encoding.HexEncoder.decode(nonce_hex)

        secret_box = nacl.secret.SecretBox(secret, encoder=nacl.encoding.HexEncoder)

        return secret_box.decrypt(text, nonce)

    @staticmethod
    def api_request(method, endpoint, data, session: PsonoServerSession):
        """
        Static API Request helper that will also automatically decrypt the content if a session secret was provided.
        Will return the decrypted content.

        """

        if session.token:
            headers = {'content-type': 'application/json', 'authorization': 'Token ' + session.token}
        else:
            headers = {'content-type': 'application/json'}
        if session and session.secret_key and data is not None:
            data = json.dumps(__class__.encrypt_symmetric(data,session.secret_key))
        r = requests.request(method, session.server.server_url + endpoint, data=data, headers=headers, verify=session.server.ssl_verify)

        if not session.secret_key:
            return_data =  r.json()
        else:
            encrypted_content = r.json()
            decrypted_content = __class__.decrypt_symmetric(encrypted_content['text'], encrypted_content['nonce'], session.secret_key)
            return_data =  json.loads(decrypted_content)

        if 'throttle' in return_data.get('detail',''):
            raise PsonoException(f"Request was throttled {return_data}")
        return return_data
    

    @staticmethod
    def _index_datastore_item_paths(datastore: PsonoDataStore):
        __class__._search_folder(search_type='pathindex',folder=datastore)

        
    
    @staticmethod
    def add_item_to_datastore(datastore:PsonoDataStoreFolder,secret:PsonoSecret):
        
        splitpath = secret.relative_path.split('/')
        folder = "/".join(splitpath[:-1])
        name = splitpath[-1]
        item = PsonoDataStoreItem(
            id=secret.link_id,
            name=name,
            type=secret.type,
            secret_id=secret.secret_id,
            secret_key=secret.secret_key
        )
        folderdata = __class__.get_folder(datastore,folder,create=True)
        folderdata.items.append(item)
    
    @staticmethod
    def remove_item_from_datastore(datastore:PsonoDataStoreFolder,secret:PsonoSecret):
        # This simply marks the item as deleted - this is all that is necessary.
        splitpath = secret.relative_path.split('/')
        folder = "/".join(splitpath[:-1])
        name = splitpath[-1]
        folderdata = __class__.get_folder(datastore,folder,create=True)
        for index,item in enumerate(folderdata.items):
            if item.name == name and not item.deleted:
                item.deleted=True
                
        

 
    @staticmethod
    def get_folder(datastore: PsonoDataStore,folder: str,create=False) -> PsonoDataStoreFolder:
        '''Gets a folder from a datastore - and optionally creates it and parents if it doesn't exist'''
        logger = logging.getLogger(__name__)
        partialpath = list()
        previouspath = datastore
        if folder=="":
            return datastore
        for folderpart in folder.split('/'):
            partialpath.append(folderpart)
            logger.debug(f"Checking folder {"/".join(partialpath)} of total path {folder} in {datastore.name}")
            try:
                thispath,traversedpath = __class__.get_datastore_path(datastore,"/".join(partialpath))
            except:
                if (create):
                    logger.debug(f"Creating path {folderpart} in folder {previouspath.relative_path} in datastore {datastore.name}")
                    thispath = __class__.create_folder(previouspath,folderpart)
                    # print("--------------folder-----------")
                    # print(previouspath)
                    # print("--------------datastore-----------")
                    # print(datastore)
                else:
                    raise PsonoPathNotFoundException
            previouspath = thispath
        
        return previouspath
    #@staticmethod
    #def create_one_folder_in_path(datastore: PsonoDataStore,folder: str) -> PsonoDataStoreFolder:
    #    if __class__.get_folder(datastore,folder,create=True) is None:
    #        return True
    #    else:
    #        return False

    @staticmethod
    def create_folder(datastore: PsonoDataStore,foldername) -> PsonoDataStoreFolder:
        newfolder = PsonoDataStoreFolder(
            id=str(uuid.uuid4()),
            name=foldername,
            relative_path=datastore.path + '/' + foldername,
            path=datastore.path + '/' + foldername
        )
        datastore.folders.append(newfolder)
        return newfolder
    @staticmethod
    def get_metadata_for_id(searchtype: str, search_data: str,datastores: List[PsonoDataStore]):
        for datastore in datastores:
            secret_metadata = __class__._search_folder(searchtype,datastore,search_data)
            if secret_metadata is not None:
                return secret_metadata

        raise PsonoIDNotFoundException(f"Cannot find {searchtype} with \"{search_data}\" in any path")
    
    @staticmethod
    def search_urlfilter(url: str,datastores: List[PsonoDataStore]) -> PsonoDataStoreItem:
        returndata = list()
        for datastore in datastores:
            search_results = __class__._search_folder('urlfilter',datastore,url)
            returndata.extend(search_results)
        return returndata
    
    @staticmethod
    def _search_folder(search_type: str,folder: PsonoDataStoreFolder,search_item=None) -> Union[PsonoDataStoreItem,List[PsonoDataStoreItem],None]:
        '''' Search folder - search types are sharelist,urlfilter,share_id,and secret_id'''
        if  search_type in ['sharelist','urlfilter']:
            search_return = 'multiple'
            returndata = list()
        else:
            search_return = 'first'
        # This will give odd results if you search a share without indexing it first
        # Solution - don't do this! That's why this is an internal method!
        if folder.path is None or folder.path == '/Default':
            folder.path = ''
        if folder.relative_path is None:
            folder.relative_path = ''

        for subfolder in folder.folders:
            if folder.path != '':
                subfolder.path = folder.path + '/' + subfolder.name
            else:
                subfolder.path = subfolder.name
            
            if folder.relative_path == '':
                subfolder.relative_path = subfolder.name
            else:
                subfolder.relative_path = folder.relative_path + '/' + subfolder.name
                
            if  subfolder.deleted:
                continue
            # We always index, because we want to know

            if search_type == 'sharelist' and subfolder.share_id:
                subfolder.path = ''
                returndata.append(subfolder)
                continue
            if search_type=='share_id' and subfolder.share_id == search_item:
                return subfolder
                                   
            subreturn = __class__._search_folder(search_type,subfolder,search_item)
            
            if subreturn is not None and search_return == 'first':
                return subreturn
            
            if search_return =='multiple':
                returndata.extend(subreturn)
        
        for  itemdata in folder.items:
            itemdata.relative_path = folder.relative_path + '/' + itemdata.name
            itemdata.path = folder.path + '/' + itemdata.name
            if itemdata.deleted:
                continue
            if search_type=='secret_id' and itemdata.secret_id == search_item:
                return itemdata
            if search_type=='urlfilter' and itemdata.urlfilter == search_item:
                returndata.append(itemdata)
                
        if search_return =='multiple':
            return returndata

        return None
        
    @staticmethod
    def get_sharelist(datastore: PsonoDataStore) -> List[PsonoDataStoreItem]:
        return __class__._search_folder('sharelist',datastore)
        
        
    
    @staticmethod
    def get_datastore_path(datastore:PsonoDataStoreFolder,folder: str,traversedpath=''):
        folderpath = folder.split('/')
        end = False
        if len(folderpath) == 1 or folderpath[-1] == "":
            end = True

        for folderdata in datastore.folders:
            if folderdata.name == folderpath[0] and not folderdata.deleted:
                # it's a share, so we stop and return the share.
                if folderdata.share_id is not None:
                    traversedpath = traversedpath + folderpath[0] + "/"
                    return folderdata,traversedpath
                # we have reached the end
                elif end:
                    traversedpath = traversedpath + folderpath[0] + "/"
                    return folderdata,traversedpath
                # it's a folder, so we keep going
                else:
                    traversedpath = traversedpath + folderpath[0] + "/"
                    return __class__.get_datastore_path(folderdata,"/".join(folderpath[1:]),traversedpath)

        for itemdata in datastore.items:
            if itemdata.name == folderpath[0]:
                return itemdata,traversedpath
        raise PsonoPathNotFoundException(f"Cannot find \"{folderpath[0]}\" in \"{traversedpath}\" {datastore}")
    
    @staticmethod
    def _get_share_secret(datastore: PsonoDataStore,folderid):
        for shareindex in datastore.share_index.values():
            if folderid in shareindex.paths:
                return shareindex.secret_key
    
    @staticmethod
    def get_datastore(datastore_id,session: PsonoServerSession) -> Union[PsonoDataStore,PsonoEnvironmentVariables]:
        """
        :param datastore_id:
        :type datastore_id:
        :return:
        :rtype:
        """

        method = 'GET'
        endpoint = '/datastore/' + datastore_id + '/'
        datastore_return = __class__.api_request(method, endpoint,None,session)        
        
        datastore_data =  json.loads(__class__.decrypt_data(datastore_return,session))
        if  isinstance(datastore_data,list):
            return PsonoEnvironmentVariables(datastore_data)
        datastore_data['secret_key'] = __class__.decrypt_secret_key(datastore_return,session)
        return PsonoDataStore(**datastore_data)



    def translate_secret_data(secret_data: dict,metadata: PsonoDataStoreItem) -> PsonoSecret:
        SecretClass = psono_type_map[metadata.type]
        secret_data['path'] = metadata.path
        secret_data['relative_path'] = metadata.relative_path
        secret_data['secret_id'] = metadata.secret_id
        secret_data['secret_key'] = metadata.secret_key
        secret_data['link_id'] = metadata.id
        secret_data['autosubmit'] = metadata.autosubmit
        secret_data['type'] = metadata.type
        psonosecret = SecretClass(**secret_data)
        return psonosecret


    def decrypt_secret_key(encrypted_item: dict,session: PsonoServerSession):
        if 'secret_key_nonce' in encrypted_item.keys():
            return __class__.decrypt_symmetric(
                    encrypted_item['secret_key'],
                    encrypted_item['secret_key_nonce'],
                    session.user_secret_key
                )
        else:
            return encrypted_item['secret_key'].encode('utf-8')

    def decrypt_data(encrypted_item: dict,session: PsonoServerSession):
        secret_key = __class__.decrypt_secret_key(encrypted_item,session)
        return __class__.decrypt_symmetric(
            encrypted_item['data'],
            encrypted_item['data_nonce'],
            secret_key
        )
    