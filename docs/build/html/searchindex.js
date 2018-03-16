Search.setIndex({docnames:["_generated/attempt_receive","_generated/attempt_send","_generated/communication.client","_generated/communication.contact","_generated/communication.contact_manager","_generated/communication.encrypted_messenger","_generated/communication.exceptions","_generated/communication.igdc","_generated/communication.messenger","_generated/communication.network","_generated/communication.protocol","_generated/communication.server","_generated/communication.socket_manager","_generated/config","_generated/encryption.crypter","_generated/encryption.exceptions","_generated/interface","_generated/keys","_generated/keys.utils","_generated/main","_generated/modules","_generated/temp","_generated/tests","_generated/tests.communication","_generated/tests.communication.client_mock","_generated/tests.communication.server_mock","_generated/tests.communication.test_client","_generated/tests.communication.test_contact","_generated/tests.communication.test_messenger","_generated/tests.communication.test_server","_generated/tests.communication.test_socket_manager","_generated/tests.encryption","_generated/tests.encryption.test_crypter","_generated/ui.app","_generated/ui.application","_generated/ui.widgets","_generated/ui.widgets.dark_shadow_effect","_generated/ui.widgets.default_dialog","_generated/ui.widgets.skinned_title_bar","_generated/user","_static/communication","_static/communication_protocols","_static/encryption","_static/encryption_protocols","_static/systems","_static/ui","index"],envversion:53,filenames:["_generated\\attempt_receive.rst","_generated\\attempt_send.rst","_generated\\communication.client.rst","_generated\\communication.contact.rst","_generated\\communication.contact_manager.rst","_generated\\communication.encrypted_messenger.rst","_generated\\communication.exceptions.rst","_generated\\communication.igdc.rst","_generated\\communication.messenger.rst","_generated\\communication.network.rst","_generated\\communication.protocol.rst","_generated\\communication.server.rst","_generated\\communication.socket_manager.rst","_generated\\config.rst","_generated\\encryption.crypter.rst","_generated\\encryption.exceptions.rst","_generated\\interface.rst","_generated\\keys.rst","_generated\\keys.utils.rst","_generated\\main.rst","_generated\\modules.rst","_generated\\temp.rst","_generated\\tests.rst","_generated\\tests.communication.rst","_generated\\tests.communication.client_mock.rst","_generated\\tests.communication.server_mock.rst","_generated\\tests.communication.test_client.rst","_generated\\tests.communication.test_contact.rst","_generated\\tests.communication.test_messenger.rst","_generated\\tests.communication.test_server.rst","_generated\\tests.communication.test_socket_manager.rst","_generated\\tests.encryption.rst","_generated\\tests.encryption.test_crypter.rst","_generated\\ui.app.rst","_generated\\ui.application.rst","_generated\\ui.widgets.rst","_generated\\ui.widgets.dark_shadow_effect.rst","_generated\\ui.widgets.default_dialog.rst","_generated\\ui.widgets.skinned_title_bar.rst","_generated\\user.rst","_static\\communication.rst","_static\\communication_protocols.rst","_static\\encryption.rst","_static\\encryption_protocols.rst","_static\\systems.rst","_static\\ui.rst","index.rst"],objects:{"":{"interface":[16,0,0,"-"],attempt_receive:[0,0,0,"-"],attempt_send:[1,0,0,"-"],config:[13,0,0,"-"],keys:[17,0,0,"-"],tests:[22,0,0,"-"],user:[39,0,0,"-"]},"communication.client":{Client:[2,1,1,""]},"communication.client.Client":{connect:[2,2,1,""]},"communication.contact":{Contact:[3,1,1,""]},"communication.contact.Contact":{connect:[3,2,1,""],from_json:[3,2,1,""],get_pending_messages:[3,2,1,""],has_connected:[3,2,1,""],num_pending_messages:[3,2,1,""],save:[3,2,1,""],start_messenger:[3,2,1,""],stop_messenger:[3,2,1,""],tell:[3,2,1,""]},"communication.contact_manager":{ContactManager:[4,1,1,""]},"communication.contact_manager.ContactManager":{add_contact:[4,2,1,""],check_status:[4,2,1,""],connect_to_contact:[4,2,1,""],connect_to_contacts:[4,2,1,""],contact_connected:[4,2,1,""],get_contact:[4,2,1,""],get_contact_by_ip:[4,2,1,""],load_contact:[4,2,1,""],load_contacts:[4,2,1,""],update_contacts_ip:[4,2,1,""]},"communication.encrypted_messenger":{EncryptedMessenger:[5,1,1,""]},"communication.encrypted_messenger.EncryptedMessenger":{consume_message:[5,2,1,""],consume_messages:[5,2,1,""],perform_handshake:[5,2,1,""],perform_handshake_as_client:[5,2,1,""],perform_handshake_as_server:[5,2,1,""],run:[5,2,1,""],send:[5,2,1,""],wait_for_next_message:[5,2,1,""]},"communication.exceptions":{ChallengeFailureError:[6,3,1,""],ClientException:[6,3,1,""],CommandFailureError:[6,3,1,""],CommunicationException:[6,3,1,""],EncryptedMessengerException:[6,3,1,""],HandshakeFailureException:[6,3,1,""],HandshakeTimeoutException:[6,3,1,""],MessengerException:[6,3,1,""],NetworkException:[6,3,1,""],ServerException:[6,3,1,""],UnexpectedResponseError:[6,3,1,""],UserDoesNotExistError:[6,3,1,""]},"communication.igdc":{FakeSocket:[7,1,1,""],IGDClient:[7,1,1,""],IGDPortOpener:[7,1,1,""],UPNPError:[7,3,1,""],get1stTagText:[7,4,1,""],getProtoId:[7,4,1,""],httpparse:[7,4,1,""],inet_ntop:[7,4,1,""],inet_pton:[7,4,1,""],isLLA:[7,4,1,""],isv6:[7,4,1,""],parseErrMsg:[7,4,1,""],sockaddr:[7,1,1,""],str2bool:[7,4,1,""]},"communication.igdc.FakeSocket":{makefile:[7,2,1,""]},"communication.igdc.IGDClient":{AddPortMapping:[7,2,1,""],DeletePortMapping:[7,2,1,""],discovery:[7,2,1,""],sendSOAP:[7,2,1,""]},"communication.igdc.IGDPortOpener":{add_port_mapping:[7,2,1,""],delete_port_mapping:[7,2,1,""],discover:[7,2,1,""]},"communication.igdc.sockaddr":{ipv4_addr:[7,5,1,""],ipv6_addr:[7,5,1,""],sa_family:[7,5,1,""]},"communication.messenger":{Messenger:[8,1,1,""]},"communication.messenger.Messenger":{consume_message:[8,2,1,""],consume_messages:[8,2,1,""],message_callback:[8,2,1,""],num_pending_messages:[8,2,1,""],raise_last_error_if_any:[8,2,1,""],recv:[8,2,1,""],run:[8,2,1,""],send:[8,2,1,""],set_message_callback:[8,2,1,""],stop:[8,2,1,""]},"communication.network":{Network:[9,1,1,""]},"communication.network.Network":{EXISTING_USER_ERROR:[9,5,1,""],FAILED_CHALLENGE_ERROR:[9,5,1,""],NO_CHALLENGE_ERROR:[9,5,1,""],NO_USER_ERROR:[9,5,1,""],OK_RESPONSE:[9,5,1,""],connect:[9,2,1,""],fetch_contact_ips:[9,2,1,""],fetch_peer:[9,2,1,""],fetch_peer_ip:[9,2,1,""],get_peer_info:[9,2,1,""],get_peer_ip:[9,2,1,""],has_peer:[9,2,1,""],raise_on_wrong_http_code:[9,2,1,""],register:[9,2,1,""]},"communication.server":{Server:[11,1,1,""]},"communication.server.Server":{listen:[11,2,1,""]},"communication.socket_manager":{SocketManager:[12,1,1,""]},"communication.socket_manager.SocketManager":{close:[12,2,1,""]},"encryption.crypter":{Crypter:[14,1,1,""],DEFAULT_PADDING:[14,4,1,""],OPENSSL_PADDING:[14,4,1,""]},"encryption.crypter.Crypter":{decrypt_key:[14,2,1,""],decrypt_message:[14,2,1,""],encrypt_key:[14,2,1,""],encrypt_message:[14,2,1,""],gen_and_set_aes_key:[14,2,1,""],gen_and_set_rsa_key:[14,2,1,""],gen_hmac:[14,2,1,""],get_public_key_pem:[14,2,1,""],load_rsa_key:[14,2,1,""],set_public_key_from_pem:[14,2,1,""],sign:[14,2,1,""],verify_signature:[14,2,1,""]},"encryption.exceptions":{BackendException:[15,3,1,""],CorruptedMessageException:[15,3,1,""],CrypterException:[15,3,1,""],InvalidSignature:[15,3,1,""],NoKeyException:[15,3,1,""]},"interface":{Interface:[16,1,1,""]},"interface.Interface":{displayInputs:[16,2,1,""],goToStart:[16,2,1,""],readInput:[16,2,1,""],run:[16,2,1,""],stop:[16,2,1,""],writeStartSymbol:[16,2,1,""]},"keys.utils":{gen_key_paths:[18,4,1,""],generate_new_key:[18,4,1,""],get_public_pem:[18,4,1,""],load_key:[18,4,1,""],load_private_key:[18,4,1,""],load_public_key:[18,4,1,""],new_key:[18,4,1,""],save_keys:[18,4,1,""]},"tests.communication":{client_mock:[24,0,0,"-"],server_mock:[25,0,0,"-"],test_client:[26,0,0,"-"],test_contact:[27,0,0,"-"],test_messenger:[28,0,0,"-"],test_server:[29,0,0,"-"],test_socket_manager:[30,0,0,"-"]},"tests.communication.client_mock":{ClientMock:[24,1,1,""]},"tests.communication.server_mock":{ServerMock:[25,1,1,""]},"tests.communication.test_client":{TestClient:[26,1,1,""]},"tests.communication.test_client.TestClient":{test_connect_no_server:[26,2,1,""],test_connect_success:[26,2,1,""]},"tests.communication.test_contact":{TestContact:[27,1,1,""]},"tests.communication.test_contact.TestContact":{test_connect:[27,2,1,""],test_from_json:[27,2,1,""],test_has_connected:[27,2,1,""],test_save:[27,2,1,""],test_start_messenger:[27,2,1,""],test_stop_messenger:[27,2,1,""]},"tests.communication.test_messenger":{Temp:[28,1,1,""]},"tests.communication.test_messenger.Temp":{setUpTestClient:[28,2,1,""],test_enter_client_connection_success:[28,2,1,""],test_exit:[28,2,1,""],test_recv:[28,2,1,""],test_send_not_connected:[28,2,1,""],test_send_success:[28,2,1,""],test_start_client_connection_no_host:[28,2,1,""],test_start_server_connection:[28,2,1,""]},"tests.communication.test_server":{TestServer:[29,1,1,""]},"tests.communication.test_server.TestServer":{test_listen_port_used:[29,2,1,""],test_listen_success:[29,2,1,""]},"tests.communication.test_socket_manager":{SocketMock:[30,1,1,""],TestException:[30,3,1,""],TestSocketManager:[30,1,1,""]},"tests.communication.test_socket_manager.SocketMock":{close:[30,2,1,""],shutdown:[30,2,1,""]},"tests.communication.test_socket_manager.TestSocketManager":{test_enter:[30,2,1,""],test_exit_no_error:[30,2,1,""],test_exit_oserror:[30,2,1,""],test_exit_other_error:[30,2,1,""]},"tests.encryption":{test_crypter:[32,0,0,"-"]},"tests.encryption.test_crypter":{TestCrypter:[32,1,1,""]},"tests.encryption.test_crypter.TestCrypter":{mockRNG:[32,2,1,""],setUp:[32,2,1,""],test_decrypt_key_no_key:[32,2,1,""],test_decrypt_key_success:[32,2,1,""],test_decrypt_key_wrong_key:[32,2,1,""],test_decrypt_message_auth_comprommised:[32,2,1,""],test_decrypt_message_no_key:[32,2,1,""],test_decrypt_message_success:[32,2,1,""],test_encrypt_key_no_key:[32,2,1,""],test_encrypt_key_success:[32,2,1,""],test_encrypt_key_wrong_key:[32,2,1,""],test_encrypt_message_no_key:[32,2,1,""],test_encrypt_message_success:[32,2,1,""],test_gen_and_set_aes_key:[32,2,1,""],test_load_rsa_key_no_file:[32,2,1,""],test_load_rsa_key_success:[32,2,1,""],test_load_rsa_key_unknown_type:[32,2,1,""]},"user.User":{add_contact:[39,2,1,""],connect:[39,2,1,""],register:[39,2,1,""],save:[39,2,1,""],say:[39,2,1,""],set_active_contact:[39,2,1,""],username:[39,5,1,""]},communication:{client:[2,0,0,"-"],contact:[3,0,0,"-"],contact_manager:[4,0,0,"-"],encrypted_messenger:[5,0,0,"-"],exceptions:[6,0,0,"-"],igdc:[7,0,0,"-"],messenger:[8,0,0,"-"],network:[9,0,0,"-"],protocol:[10,0,0,"-"],server:[11,0,0,"-"],socket_manager:[12,0,0,"-"]},encryption:{crypter:[14,0,0,"-"],exceptions:[15,0,0,"-"]},keys:{utils:[18,0,0,"-"]},tests:{communication:[23,0,0,"-"],encryption:[31,0,0,"-"]},ui:{widgets:[35,0,0,"-"]},user:{User:[39,1,1,""]}},objnames:{"0":["py","module","Python module"],"1":["py","class","Python class"],"2":["py","method","Python method"],"3":["py","exception","Python exception"],"4":["py","function","Python function"],"5":["py","attribute","Python attribute"]},objtypes:{"0":"py:module","1":"py:class","2":"py:method","3":"py:exception","4":"py:function","5":"py:attribute"},terms:{"1st":7,"boolean":9,"byte":14,"case":[26,27,29,30,32],"class":[2,3,4,5,7,8,9,11,12,14,16,24,25,26,27,28,29,30,32,39],"default":[8,16],"function":[8,9,14],"new":[8,14,46],"public":[3,5,9,14],"return":[3,4,5,7,8,9,14,16],"true":7,"try":4,"while":[5,8],AES:14,One:3,The:[2,3,4,5,8,9,11,12,14,39],There:9,Will:8,_ctype:7,_io:7,action:7,actionargu:7,actionnam:7,activ:39,add:[4,39],add_contact:[4,39],add_port_map:7,addportmap:7,addr:7,address:[2,7,11],address_famili:7,after:5,all:[3,4,5,7,8,9],allow:4,along:14,alreadi:9,alwai:8,ani:[3,8],anoth:8,answer:9,api:[9,46],app:[45,46],applic:[39,45,46],aren:3,arg:7,asynchron:11,attempt:[3,5,9,28],attempt_rec:20,attempt_send:20,authent:[5,9,14,46],author:14,backend:14,backendexcept:[14,15],base:[2,3,4,5,6,7,8,9,11,12,14,15,16,24,25,26,27,28,29,30,32,39],been:14,befor:32,bind:11,bodi:7,bstr:7,buffer:16,call:[3,8,11,16],callback:[8,11],can:[4,8,9],challeng:9,challengefailureerror:[6,9],charact:16,check:[3,9],check_statu:4,cipher:14,client:[3,5,7,28,40,46],client_mock:23,clientexcept:[2,6],clientmock:24,close:[12,30],code:[7,9,39],command:16,commandfailureerror:[6,9],commun:46,communicationexcept:6,config:20,connect:[2,3,4,5,8,9,11,12,28,39,46],connect_to_contact:4,construct:[41,43,44],consum:8,consume_messag:[5,8],contact:[4,5,9,39,40,46],contact_connect:4,contact_data:3,contact_dir:4,contact_fil:4,contact_kei:5,contact_manag:39,contact_nam:[3,4],contact_public_kei:5,contactmanag:4,contain:3,content:20,continu:[5,8],control:7,controlurl:7,corruptedmessageexcept:[14,15],creat:[3,9],creation:16,credenti:39,crypter:[5,42,46],crypterexcept:[14,15],cryptograph:14,ctrlurl:7,current:[5,8,14,39],dark_shadow_effect:35,data:[3,4,5,9,14],deal:8,decrypt:[5,14,46],decrypt_kei:14,decrypt_messag:14,default_dialog:35,default_pad:14,defin:3,delete_port_map:7,deleteportmap:7,desc:7,descript:7,desktop:39,devic:7,did:14,directori:[3,4,9,14,18],discov:7,discoveri:7,displai:16,displayinput:16,document:5,doe:[4,5,8,14],durat:7,edebug:7,empti:[3,8],enabl:7,encod:16,encrypt:[5,40,46],encrypt_kei:14,encrypt_messag:14,encrypted_kei:14,encrypted_messag:14,encryptedmessag:39,encryptedmesseng:5,encryptedmessengerexcept:6,endpoint:9,ensur:14,eras:16,err_resp:7,error:[3,4,5,7,8,9,30],except:[2,7,30,40,42,46],exchang:5,exercis:32,exist:[4,5,9,12,14,39],existing_user_error:9,extport:7,fail:9,failed_challenge_error:9,faill:9,fakesocket:7,fals:7,fetch:[4,5,9],fetch_contact_ip:9,fetch_peer:9,fetch_peer_ip:9,fetcher:16,file:[4,14],filenotfounderror:4,find:7,first:8,fixtur:32,flag:16,friend:39,from:[3,4,5,8,14,16,39],from_json:3,func:9,garante:14,gen_and_set_aes_kei:14,gen_and_set_rsa_kei:14,gen_hmac:14,gen_key_path:18,gener:14,generate_new_kei:18,get1sttagtext:7,get:[7,14],get_contact:4,get_contact_by_ip:4,get_peer_info:9,get_peer_ip:9,get_pending_messag:3,get_public_key_pem:14,get_public_pem:18,getprotoid:7,given:[2,4,5,8,14],gotostart:16,hand:8,handhsak:14,handl:[2,3,4,5,8,11,12,14,16],handle_incoming_connect:11,handleincom:16,handleoutgo:16,handshak:[3,5,14,46],handshakefailureexcept:6,handshaketimeoutexcept:[5,6],has:[3,4,9],has_connect:3,has_peer:9,hasn:14,have:8,hcode:7,hideerr:7,him:3,his:[9,39],hmac:14,hold:[9,14],hook:32,host:[2,11,24,25],hostnam:7,how:3,http:[7,9],httppars:7,ident:14,identif:9,igd:7,igdclient:7,igdportopen:7,incom:[8,11],incomig:16,indefinit:11,index:46,indic:9,inet_ntop:7,inet_pton:7,info:[9,46],inform:9,inhandleperiod:16,initi:[5,14],input:16,instanc:3,integr:14,interfac:20,intip:7,intport:7,invalidsignatur:[14,15],ip_str:7,ips:[4,9],ipv4_addr:7,ipv6:7,ipv6_addr:7,islla:7,issu:[5,8],isv6:7,its:[7,14,16],json:[3,4,9],just:4,kei:[3,5,9,14,20,39],key_dir:9,key_typ:14,key_util:39,kind:8,last:[8,9],latest:5,lifecycl:12,line:16,linebreak:16,link:7,list:[3,4,8,9,39],listen:[8,11],load:[4,14],load_contact:4,load_kei:18,load_private_kei:18,load_public_kei:18,load_rsa_kei:14,local:7,logic:2,look:9,loop:16,main:[16,20,46],makefil:7,manag:[4,9,11,12,40,46],mani:3,match:[4,14],member:7,merg:14,messag:[3,4,5,7,8,9,14,16,39,46],message_callback:8,messeng:[5,40,46],messengerexcept:[6,8],method:32,methodnam:[26,27,29,30,32],might:8,mockrng:32,modul:[20,46],multicast:7,multipl:4,must:14,name:[3,4,9,39],necessari:[3,8],need:14,netsec:39,network:[40,46],networkexcept:[6,9],new_kei:18,no_challenge_error:9,no_user_error:9,nokeyexcept:[14,15],none:[3,4,7,8,12],noth:8,num_pending_messag:[3,8],number:3,numbyt:32,object:[2,3,4,7,8,9,12,14,16,24,25,28,30,39],occur:8,ok_respons:9,one:[3,16],ongo:3,open:2,openssl_pad:14,option:12,oserror:5,other:[8,9],our:3,out:5,outgo:2,output:16,over:[5,8],overwrit:8,overwriten:8,owner:[3,4],owner_nam:[3,4],packag:20,packed_ip:7,page:46,pair:14,paramet:[2,3,4,5,8,9,11,12,14],pars:7,parseerrmsg:7,pass:[3,16],peer:[4,9,39,46],peer_registri:[4,39],pem:14,pem_data:14,pend:[3,5],perform:[5,14],perform_handshak:5,perform_handshake_as_cli:5,perform_handshake_as_serv:5,period:5,port:[2,7,11,24,25],pprint:7,privat:[5,9,14,39],private_kei:[5,14,18,39],process:8,proto:7,proto_nam:7,protocol:[7,40,46],public_kei:[3,14],public_key_data:18,public_pem:9,queue:8,rais:[2,3,4,5,8,9,14],raise_last_error_if_ani:8,raise_on_wrong_http_cod:9,random:14,raw_kei:14,read:16,readinput:16,reason:30,receiv:[5,8,16,46],recept:8,record:9,recv:8,regist:[9,39,46],registri:[4,39],regularli:16,remot:[8,16],remotehost:7,request:7,resourc:9,respons:7,result:16,reurn:7,right:14,rng:14,role:[3,5],rsa:14,run:[5,8,16],runtest:[26,27,29,30,32],sa_famili:7,sai:39,said:3,save:[3,39],save_dir:3,save_kei:18,search:46,secret:14,secur:14,send:[3,5,7,8,39,46],sendsoap:7,serial:14,server:[3,5,28,40,46],server_mock:23,serverexcept:6,servermock:25,servic:7,servicetyp:7,session:[3,4,5,46],set:[14,16,28,32],set_active_contact:39,set_message_callback:8,set_public_key_from_pem:14,setup:32,setuptestcli:28,should:[3,5],shutdown:30,sign:14,signatur:14,size:14,skinned_title_bar:35,soap:7,sockaddr:7,socket:[2,3,4,5,8,11,12,40,46],socket_manag:[2,11],socketmanag:[2,11,12],socketmock:30,solv:9,sourc:[2,3,4,5,6,7,8,9,11,12,14,15,16,18,24,25,26,27,28,29,30,32,39],specif:9,specifi:[3,9,14],start:[3,4,5,8,16,46],start_messeng:3,statu:9,stdin:16,stop:[3,8,16],stop_messeng:3,store:[4,9,14],str2bool:7,string:[4,5,9,14],stringio:7,structur:7,submodul:20,support:[7,14],symbol:16,symmetr:14,system:46,tag:7,tagname_list:7,take:[5,11],tell:3,temp:28,test:20,test_client:23,test_connect:27,test_connect_no_serv:26,test_connect_success:26,test_contact:23,test_crypt:31,test_decrypt_key_no_kei:32,test_decrypt_key_success:32,test_decrypt_key_wrong_kei:32,test_decrypt_message_auth_comprommis:32,test_decrypt_message_no_kei:32,test_decrypt_message_success:32,test_encrypt_key_no_kei:32,test_encrypt_key_success:32,test_encrypt_key_wrong_kei:32,test_encrypt_message_no_kei:32,test_encrypt_message_success:32,test_ent:30,test_enter_client_connection_success:28,test_exit:28,test_exit_no_error:30,test_exit_oserror:30,test_exit_other_error:30,test_from_json:27,test_gen_and_set_aes_kei:32,test_has_connect:27,test_listen_port_us:29,test_listen_success:29,test_load_rsa_key_no_fil:32,test_load_rsa_key_success:32,test_load_rsa_key_unknown_typ:32,test_messeng:23,test_recv:28,test_sav:27,test_send_not_connect:28,test_send_success:28,test_serv:23,test_socket_manag:23,test_start_client_connection_no_host:28,test_start_messeng:27,test_start_server_connect:28,test_stop_messeng:27,testcas:[26,27,29,30,32],testclient:26,testcontact:27,testcrypt:32,testexcept:30,testserv:29,testsocketmanag:30,them:8,thi:[5,8],thing:14,thread:[8,16,46],time:5,todo:5,transmiss:5,tri:5,two:16,type:[14,18],ucod:7,udes:7,unabl:2,under:[41,43,44],unexpect:9,unexpectedresponseerror:[6,9],unicod:5,union:7,unittest:[26,27,29,30,32],until:5,updat:9,update_contacts_ip:4,upnp:7,upnperror:7,url:[7,9],use:3,used:[3,14],user:[3,4,5,8,9,14,20,46],userdoesnotexisterror:[6,9],usernam:[4,9,18,39],using:14,utf8:16,util:[14,17,20,39],valid:5,valu:[3,7],valueerror:[3,5],vector:14,verifi:14,verify_signatur:14,via:7,wait:5,wait_for_next_messag:5,wanipc:7,want:[4,9],wasn:14,when:[2,3,8,9],where:4,whether:[3,5,9],which:[3,4,5,8,9,11,12,14,28],whom:5,whose:[4,9],without:16,work:5,write:16,writestartsymbol:16,xml:7,yet:14,you:9},titles:["attempt_receive module","attempt_send module","communication.client module","communication.contact module","communication.contact_manager module","communication.encrypted_messenger module","communication.exceptions module","communication.igdc module","communication.messenger module","communication.network module","communication.protocol module","communication.server module","communication.socket_manager module","config module","encryption.crypter module","encryption.exceptions module","interface module","keys package","keys.utils module","main module","EncryptedMessaging","temp module","tests package","tests.communication package","tests.communication.client_mock module","tests.communication.server_mock module","tests.communication.test_client module","tests.communication.test_contact module","tests.communication.test_messenger module","tests.communication.test_server module","tests.communication.test_socket_manager module","tests.encryption package","tests.encryption.test_crypter module","ui.app module","ui.application module","ui.widgets package","ui.widgets.dark_shadow_effect module","ui.widgets.default_dialog module","ui.widgets.skinned_title_bar module","user module","Communication package","Encryption Protocols","Encryption package","Encryption Protocols","Systems","ui package","Welcome to EncryptedMessenger\u2019s documentation!"],titleterms:{"new":44,app:33,applic:34,attempt_rec:0,attempt_send:1,authent:43,client:2,client_mock:24,commun:[2,3,4,5,6,7,8,9,10,11,12,23,24,25,26,27,28,29,30,40],config:13,connect:44,contact:3,contact_manag:4,content:[17,22,23,31,35,41,43,44],crypter:14,dark_shadow_effect:36,decrypt:43,default_dialog:37,document:46,encrypt:[14,15,31,32,41,42,43],encrypted_messeng:5,encryptedmessag:20,encryptedmesseng:46,except:[6,15],guest:44,handshak:43,host:44,igdc:7,indic:46,interfac:16,kei:[17,18],main:[19,44],messag:[41,43,44],messeng:8,modul:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39],network:[9,43,44],packag:[17,22,23,31,35,40,42,45],peer:[43,44],protocol:[10,41,43],receiv:41,regist:44,send:41,server:11,server_mock:25,session:44,skinned_title_bar:38,socket_manag:12,start:44,submodul:[17,23,31,35],system:44,tabl:46,temp:21,test:[22,23,24,25,26,27,28,29,30,31,32],test_client:26,test_contact:27,test_crypt:32,test_messeng:28,test_serv:29,test_socket_manag:30,thread:44,user:[39,44],util:18,welcom:46,widget:[35,36,37,38]}})