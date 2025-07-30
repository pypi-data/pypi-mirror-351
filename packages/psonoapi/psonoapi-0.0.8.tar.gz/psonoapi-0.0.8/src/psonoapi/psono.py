from .psonoapihelper import PsonoAPIHelper
from .datamodels import *
from .exceptions import *
import nacl,json,os,logging,uuid,deepdiff,copy

#TODO - add optional caching
class PsonoAPI:
    def __init__(self,options = dict(),serverconfig: PsonoServerConfig = None,login: bool = True):
        cleanoptions = copy.copy(options)
        for option in options:
            if options[option] is None:
                del cleanoptions[option]

        myoptions = cleanoptions | dict(os.environ)
        if serverconfig is None:
            serverconfig = PsonoServerConfig(**myoptions)
        self.session = PsonoServerSession(server=serverconfig)
        self.logger = logging.getLogger(__name__)
        if login:
            self.login()

    def _api_request(self,method: str,endpoint: str,data = None):
        return PsonoAPIHelper.api_request(method,endpoint,data,self.session)
    
    def _list_datastores(self,store_type: str = 'password') -> Dict[str,dict]:
        # Simple list of datastores, not encrypted
        endpoint = '/datastore/'
        datastore_return = self._api_request('GET', endpoint)             
        content = dict()
        for datastore_info in datastore_return['datastores']:
            if datastore_info['type'] == store_type:
                content[datastore_info['id']] = datastore_info
        return content

    def _write_store(self,store: Union[PsonoDataStore,PsonoShareStore]):
        if isinstance(store,PsonoShareStore):
            return self._write_share(store)
        else:
            return self._write_datastore(store)
        
    def _write_share(self,sharestore: PsonoShareStore):
       method = 'PUT'
       endpoint = '/share/'
       encrypted_store = PsonoAPIHelper.encrypt_symmetric(sharestore.psono_dump_json(), sharestore.share_secret_key)
       data = json.dumps({
            'share_id': sharestore.share_id,
            'data': encrypted_store['text'],
            'data_nonce': encrypted_store['nonce'],
       })

       return self._api_request(method, endpoint, data=data)
    
    def _write_datastore(self,datastore: PsonoDataStore):
       method = 'POST'
       endpoint = '/datastore/'
       encrypted_datastore = PsonoAPIHelper.encrypt_symmetric(datastore.psono_dump_json(), datastore.secret_key)
       data = json.dumps({
            'datastore_id': self.datastore.datastore_id,
            'data': encrypted_datastore['text'],
            'data_nonce': encrypted_datastore['nonce'],
       })

       return self._api_request(method, endpoint, data=data)

    
    def get_datastore(self,datastore_id = None) -> Union[PsonoDataStore,PsonoEnvironmentVariables]:
        datastores = self._list_datastores()
        if datastore_id is None:
            # Read content of all password datastores
            for datastore in datastores.values():
                datastore_id = datastore['id']
                break
        datastore = PsonoAPIHelper.get_datastore(datastore_id,self.session)
        datastore.name = datastores[datastore_id]['description']
        return datastore

    def delete_secret(self,secret: Union[PsonoSecret,str]):
        if isinstance(secret,str):
            path = secret
        else:
            path = secret.path
        datastore,datastorepath = self._get_store_by_path(path)
        deletesecret = copy.copy(secret)
        # Adjust the path to be where the share/datastore is.
        deletesecret.path = deletesecret.path.replace(datastorepath,'')
        # Add item to folder - this will create the folder/item if it doesn't exist.
        oldstore = copy.deepcopy(datastore)
        PsonoAPIHelper.remove_item_from_datastore(datastore,deletesecret)
        return self._write_store(datastore)

    def update_secret(self,secret: PsonoSecret):
       
        if not secret.secret_id or secret.secret_id == '' or secret.secret_id == 'new':
            existing_secret = self.get_path(secret.path)
            secret.secret_id = existing_secret.secret_id
            secret.secret_key = existing_secret.secret_key
              
        encrypted_secret = PsonoAPIHelper.encrypt_symmetric(secret.psono_dump_json(), secret.secret_key)
        
        data = json.dumps({
            'secret_id': secret.secret_id,
            'data': encrypted_secret['text'],
            'data_nonce': encrypted_secret['nonce'],
            'callback_url': '',
            'callback_user': '',
            'callback_pass': '',
        })

        secret_result = self._api_request('POST','/secret/', data=data)

        return secret_result
        
    def generate_new_secret(self,secrettype_or_secretdata : Union[str,dict]) -> PsonoSecret:
        if isinstance(secrettype_or_secretdata,str):
            secrettype = secrettype_or_secretdata
        elif isinstance(secrettype_or_secretdata,dict):
            secrettype = secrettype_or_secretdata.get('type','None')
            if 'title' not in secrettype_or_secretdata.keys():
                secrettype_or_secretdata['title'] = secrettype_or_secretdata['path'].split('/')[-1]

        if secrettype not in psono_type_list:
            raise PsonoException(f"Data type {secrettype} not a valid data type (valid types: {psono_type_list})")
        newdata = dict()
        newdata['link_id'] = str(uuid.uuid4())
        newdata['secret_id'] = 'new'
        newdata['path'] = 'new'
        newdata['type'] = secrettype
        newdata['secret_key'] = nacl.encoding.HexEncoder.encode(nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)).decode()
        
        if isinstance(secrettype_or_secretdata,dict):
            newdata = newdata | secrettype_or_secretdata
       
        newsecret=psono_type_map[secrettype](**newdata)
        return newsecret
    
    def _write_new_secret(self,secret:PsonoSecret,datastore_id: str = None,share_id: str = None):
        encrypted_secret = PsonoAPIHelper.encrypt_symmetric(secret.psono_dump_json(), secret.secret_key)
        parent_id_type= 'parent_datastore_id'
        if datastore_id is None and share_id is None:
            datastore_id = self.datastore.datastore_id
            parent_id = self.datastore.datastore_id
        elif datastore_id is not None:
            parent_id = datastore_id 
        else:
            parent_id_type= 'parent_share_id'
            parent_id = share_id 

        data = json.dumps({
            'data': encrypted_secret['text'],
            'data_nonce': encrypted_secret['nonce'],
            'link_id': secret.link_id,
            parent_id_type: parent_id,
            'callback_url': '',
            'callback_user': '',
            'callback_pass': '',
        })
        secret_result = self._api_request('PUT','/secret/', data=data)
        return secret_result
    

    def write_secret(self,secret: Union[PsonoSecret,dict],create: bool = True,datastore: PsonoDataStore = None):
        '''Given a secret or a dict that includes a path, create it or update it.'''
        if datastore is None:
            datastore = self.datastore
        existing_secret_metadata = None
        newsecret = secret
        if isinstance(secret,dict):
            newsecret = self.generate_new_secret(secret)

        returnstatus = { 'updated' : False}
        # if self.get_secret(secret.secret_id):
        #     self.update_secret(secret)
        #     return
        try:
            existing_secret_metadata = self.get_path(secret.path)
        except PsonoSecretNotFoundException:
            pass
        if isinstance(existing_secret_metadata,PsonoDataStoreFolder):
            raise Exception("Trying to write a secret that is already a folder")
        elif isinstance(existing_secret_metadata,PsonoSecret):
            returnstatus['updated'] = True
            self.update_secret(secret)
            return returnstatus
    
        if not create:
            raise PsonoException(f"Trying to write secret to {newsecret.path} but create is set to False")
        
        # we always get an up to date copy of the datastore
        datastore,datastorepath = self._get_store_by_path(newsecret.path)
        
        # TODO Need to check if the datastore is empty, because we apparently need to seed values. 
        # (i.e. it doesn't work on an empty datastore)        

        if isinstance(datastore,PsonoShareStore):
            secret_result = self._write_new_secret(newsecret,share_id=datastore.share_id)
        else:
            secret_result = self._write_new_secret(newsecret,datastore_id=datastore.datastore_id)
        
        # tell the secret what its ID is
        newsecret.secret_id = secret_result['secret_id']
        # Adjust the path to be where the share/datastore is.
        newsecret.path = newsecret.path.replace(datastorepath,'')
        # Add item to folder - this will create the folder/item if it doesn't exist.
        PsonoAPIHelper.add_item_to_datastore(datastore,newsecret)
        self._write_store(datastore)
        # Change the path back to the true path
        newsecret.path = secret.path
        # if we were provided an object, update it.
        
        if isinstance(secret,PsonoSecret):
            secret = newsecret
        return returnstatus
        

                   
        
        
        




    def _get_store_by_path(self,path,datastore: PsonoDataStore=None) -> Union[PsonoDataStore,PsonoShareStore] :
        if datastore is None:
            datastore = self.datastore
        try:
            pathdetail,traversedpath = PsonoAPIHelper.get_datastore_path(self.datastore,path)
        except:
            pathdetail = datastore
            traversedpath = ''
        if isinstance(pathdetail,PsonoDataStoreFolder) and pathdetail.share_id is not None:
            sharedatastore = self.get_share(pathdetail)
            store =  sharedatastore
        else:
            store =  datastore
            traversedpath = ''
        return (store,traversedpath)
        

    def get_path(self,path,datastore: PsonoDataStore=None,metadata_only=False) -> PsonoDataItem :
        if datastore is None:
            datastore = self.datastore
        pathdetail,traversedpath = PsonoAPIHelper.get_datastore_path(self.datastore,path)
        if isinstance(pathdetail,PsonoDataStoreItem):
            item =  self._get_secret_data(pathdetail)
        elif isinstance(pathdetail,PsonoDataStoreFolder) and pathdetail.share_id is not None:
            sharedatastore = self.get_share(pathdetail)
            substorepath = path.replace(traversedpath,'')
            subpath,traversedpath = PsonoAPIHelper.get_datastore_path(sharedatastore,substorepath)
            pathdetail = subpath
            item = self._get_secret_data(subpath)
        else:
            return pathdetail
        if metadata_only:
            return pathdetail
        item['path'] = path

        return PsonoAPIHelper.translate_secret_data(item,pathdetail)
    
    def get_share(self,share: PsonoDataStoreFolder) -> PsonoShare:
        share_return = self._api_request('GET','/share/'+ share.share_id + '/')
        if 'data' not in share_return:
            raise PsonoPermissionDeniedOrNotExistException(f"Could not access share {share}: {share_return}")
        sharedata = json.loads(PsonoAPIHelper.decrypt_symmetric(share_return['data'],share_return['data_nonce'],share.share_secret_key))
        if "share_id" not in sharedata:
            sharedata['share_id'] = share.share_id
        if "share_secret_key" not in sharedata:
            sharedata['share_secret_key'] = share.share_secret_key
        return PsonoShareStore(**sharedata)

    def _get_secret(self,secretitem: PsonoDataStoreItem):
        secret_data = self._get_secret_rawdata(secretitem)
        secret_object = PsonoAPIHelper.translate_secret_data(secret_data,secretitem)
        return secret_object
    
    def _get_secret_rawdata(self,secretitem: PsonoDataStoreItem):
        secretreturndata =  self._api_request('GET','/secret/' + secretitem.secret_id + '/')
        secretreturndata['secret_key'] = secretitem.secret_key
        secret_data = json.loads(PsonoAPIHelper.decrypt_data(secretreturndata,self.session).decode('utf-8'))
        return secret_data
    
    def get_secret(self,secret_id):
        if not self.session.user_restricted:
            return self._find_secret_by_id(secret_id)
        else:
            return PsonoException('restricted API not yet supported')
            secretreturndata =  self._api_request('GET','/secret/' + secret_id + '/')
        #secretdata = self._get_secret_data(tempsecret)
        secret_data = json.loads(PsonoAPIHelper.decrypt_data(secretreturndata,self.session).decode('utf-8'))
        #ObjectClass = PsonoTypeMap[pathdetail.type]
        #return ObjectClass(**item)  

    def _get_all_datastores(self) -> List[PsonoDataStore]:
        all_datastores = list()
        # get all the datastores
        datastore_ids = self._list_datastores().keys()
        for datastore_id in datastore_ids:
            datastore = self.get_datastore(datastore_id)
            all_datastores.append(datastore)
            for share in PsonoAPIHelper.get_sharelist(datastore):
                try: 
                    all_datastores.append(self.get_share(share))
                except PsonoPermissionDeniedOrNotExistException:
                    self.logger.warning(f"Could not access share {share.name}: {share.id}")
        return all_datastores
            

    def _find_secret_by_id(self,secret_id):
        secretmetadata =  PsonoAPIHelper.get_metadata_key_for_id(secret_id,self._get_all_datastores())
        return self._get_secret(secretmetadata)

    def search_urlfilter(self,url) -> List[PsonoSecret]:
        secretmetadatalist =  PsonoAPIHelper.search_urlfilter(url,self._get_all_datastores())
        secretlist=list()
        
        for secretmetadata in secretmetadatalist:
            secretlist.append(self._get_secret(secretmetadata))
        return secretlist

        


    def login(self):
        # 1. Generate the login info including the private key for PFS
        client_login_info = PsonoAPIHelper.generate_client_login_info(self.session)

        if True: # if logging in via apikey (no others are currently supported)
            endpoint = '/api-key/login/'
        
        json_response = PsonoAPIHelper.api_request('POST', '/api-key/login/', json.dumps(client_login_info),self.session)

        # If the signature is set, verify it
        if self.session.server.server_signature is not None:
            PsonoAPIHelper.verify_signature(json_response['login_info'],
                                          json_response['login_info_signature'],
                                          self.session.server.server_signature)
        else:
            self.logger.warning('Server signature is not set, cannot verify identity')
        
        self.session.public_key = json_response['server_session_public_key']
        decrypted_server_login_info = PsonoAPIHelper.decrypt_server_login_info(
            json_response['login_info'],
            json_response['login_info_nonce'],
            self.session
        )

        self.session.token = decrypted_server_login_info['token'] 
        self.session.secret_key = decrypted_server_login_info['session_secret_key'] 
        self.session.username = decrypted_server_login_info['user']['username']
        self.session.public_key = decrypted_server_login_info['user']['public_key'] 
        self.session.user_restricted = decrypted_server_login_info['api_key_restrict_to_secrets'] 
        

        # if the api key is unrestricted then the request will also return the encrypted secret and private key
        # of the user, symmetric encrypted with the api secret key
        if not self.session.user_restricted:
            def _decrypt_with_api_secret_key(session: PsonoServerSession,secret_hex, secret_nonce_hex):
                return PsonoAPIHelper.decrypt_symmetric(secret_hex, secret_nonce_hex, session.server.secret_key)

            self.session.user_private_key = _decrypt_with_api_secret_key(self.session,
                decrypted_server_login_info['user']['private_key'],
                decrypted_server_login_info['user']['private_key_nonce']
            )

            self.session.user_secret_key = _decrypt_with_api_secret_key(self.session,
                decrypted_server_login_info['user']['secret_key'],
                decrypted_server_login_info['user']['secret_key_nonce']
            ) 
            self.datastore = self.get_datastore()
