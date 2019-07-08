Search.setIndex({docnames:["authors","contributing","history","index","installation","modules","readme","rse_api","rse_api.controllers","rse_api.swagger","rse_api.tasks","usage"],envversion:{"sphinx.domains.c":1,"sphinx.domains.changeset":1,"sphinx.domains.cpp":1,"sphinx.domains.javascript":1,"sphinx.domains.math":1,"sphinx.domains.python":1,"sphinx.domains.rst":1,"sphinx.domains.std":1,"sphinx.ext.viewcode":1,sphinx:55},filenames:["authors.rst","contributing.rst","history.rst","index.rst","installation.rst","modules.rst","readme.rst","rse_api.rst","rse_api.controllers.rst","rse_api.swagger.rst","rse_api.tasks.rst","usage.rst"],objects:{"":{rse_api:[7,0,0,"-"]},"rse_api.cli":{add_cli:[7,1,1,""],show_routes:[7,1,1,""]},"rse_api.controllers":{simple_controller:[8,0,0,"-"]},"rse_api.controllers.simple_controller":{SimpleController:[8,2,1,""]},"rse_api.controllers.simple_controller.SimpleController":{"delete":[8,3,1,""],find_all:[8,3,1,""],find_one:[8,3,1,""],get:[8,3,1,""],methods:[8,4,1,""],post:[8,3,1,""],put:[8,3,1,""]},"rse_api.decorators":{actor:[7,1,1,""],conditional_decorator:[7,1,1,""],cron:[7,1,1,""],json_only:[7,1,1,""],register_resource:[7,1,1,""],schema_in:[7,1,1,""],schema_in_out:[7,1,1,""],schema_out:[7,1,1,""],singleton_function:[7,1,1,""],timeit_logged:[7,1,1,""]},"rse_api.errors":{RSEApiException:[7,5,1,""],register_common_error_handlers:[7,1,1,""]},"rse_api.query":{get_pagination_from_request:[7,1,1,""]},"rse_api.swagger":{decorators:[9,0,0,"-"],swagger_registry:[9,0,0,"-"],swagger_spec:[9,0,0,"-"]},"rse_api.swagger.decorators":{openapi_operation_props:[9,1,1,""],openapi_request:[9,1,1,""],openapi_response:[9,1,1,""]},"rse_api.swagger.swagger_registry":{OpenApiRegistry:[9,2,1,""],SwaggerSpecFormats:[9,2,1,""],find_rule_by_url:[9,1,1,""],find_view_func_by_url:[9,1,1,""],get_swagger_registry:[9,1,1,""],parameters_from_url:[9,1,1,""]},"rse_api.swagger.swagger_registry.OpenApiRegistry":{add_class_request:[9,3,1,""],add_class_response:[9,3,1,""],add_marshmallow_schema:[9,3,1,""],add_schema:[9,3,1,""],register_controller_resource:[9,3,1,""],render:[9,3,1,""],update_class_method_props:[9,3,1,""]},"rse_api.swagger.swagger_registry.SwaggerSpecFormats":{JSON:[9,4,1,""],YAML:[9,4,1,""]},"rse_api.swagger.swagger_spec":{IgnoreNoneIterMixin:[9,2,1,""],OpanApiSchemaCombineType:[9,2,1,""],OpenApiCallback:[9,2,1,""],OpenApiComponents:[9,2,1,""],OpenApiContact:[9,2,1,""],OpenApiDataType:[9,2,1,""],OpenApiDocument:[9,2,1,""],OpenApiEncoding:[9,2,1,""],OpenApiExample:[9,2,1,""],OpenApiExternalDocumentation:[9,2,1,""],OpenApiHeader:[9,2,1,""],OpenApiInfo:[9,2,1,""],OpenApiIntFormats:[9,2,1,""],OpenApiLicense:[9,2,1,""],OpenApiLink:[9,2,1,""],OpenApiMediaType:[9,2,1,""],OpenApiMethod:[9,2,1,""],OpenApiNumberFormats:[9,2,1,""],OpenApiOAuthFlow:[9,2,1,""],OpenApiOAuthFlows:[9,2,1,""],OpenApiParameter:[9,2,1,""],OpenApiParameterInput:[9,2,1,""],OpenApiPath:[9,2,1,""],OpenApiPathOperation:[9,2,1,""],OpenApiPaths:[9,2,1,""],OpenApiReference:[9,2,1,""],OpenApiRequestBody:[9,2,1,""],OpenApiResponse:[9,2,1,""],OpenApiResponses:[9,2,1,""],OpenApiSchema:[9,2,1,""],OpenApiSchemaCombine:[9,2,1,""],OpenApiSecurity:[9,2,1,""],OpenApiSecurityInputFrom:[9,2,1,""],OpenApiSecurityType:[9,2,1,""],OpenApiServer:[9,2,1,""],OpenApiServerVariable:[9,2,1,""],OpenApiStringFormats:[9,2,1,""],OpenApiTag:[9,2,1,""],nested_convert:[9,1,1,""]},"rse_api.swagger.swagger_spec.IgnoreNoneIterMixin":{excluded_fields:[9,4,1,""],remapped_fields:[9,4,1,""],required_fields:[9,4,1,""]},"rse_api.swagger.swagger_spec.OpanApiSchemaCombineType":{ALLOF:[9,4,1,""],ANYOF:[9,4,1,""],NOT:[9,4,1,""],ONEOF:[9,4,1,""]},"rse_api.swagger.swagger_spec.OpenApiComponents":{remapped_fields:[9,4,1,""]},"rse_api.swagger.swagger_spec.OpenApiContact":{required_fields:[9,4,1,""]},"rse_api.swagger.swagger_spec.OpenApiDataType":{ARRAY:[9,4,1,""],BOOL:[9,4,1,""],INTEGER:[9,4,1,""],NUMBER:[9,4,1,""],OBJECT:[9,4,1,""],STRING:[9,4,1,""]},"rse_api.swagger.swagger_spec.OpenApiDocument":{remapped_fields:[9,4,1,""],required_fields:[9,4,1,""]},"rse_api.swagger.swagger_spec.OpenApiEncoding":{remapped_fields:[9,4,1,""]},"rse_api.swagger.swagger_spec.OpenApiExample":{remapped_fields:[9,4,1,""]},"rse_api.swagger.swagger_spec.OpenApiExternalDocumentation":{required_fields:[9,4,1,""]},"rse_api.swagger.swagger_spec.OpenApiHeader":{remapped_fields:[9,4,1,""]},"rse_api.swagger.swagger_spec.OpenApiInfo":{remapped_fields:[9,4,1,""],required_fields:[9,4,1,""]},"rse_api.swagger.swagger_spec.OpenApiIntFormats":{INT32:[9,4,1,""],INT64:[9,4,1,""]},"rse_api.swagger.swagger_spec.OpenApiLicense":{required_fields:[9,4,1,""]},"rse_api.swagger.swagger_spec.OpenApiLink":{remapped_fields:[9,4,1,""]},"rse_api.swagger.swagger_spec.OpenApiMethod":{DELETE:[9,4,1,""],GET:[9,4,1,""],HEAD:[9,4,1,""],OPTIONS:[9,4,1,""],PATCH:[9,4,1,""],POST:[9,4,1,""],PUT:[9,4,1,""],TRACE:[9,4,1,""]},"rse_api.swagger.swagger_spec.OpenApiNumberFormats":{DOUBLE:[9,4,1,""],FLOAT:[9,4,1,""]},"rse_api.swagger.swagger_spec.OpenApiOAuthFlow":{remapped_fields:[9,4,1,""]},"rse_api.swagger.swagger_spec.OpenApiOAuthFlows":{remapped_fields:[9,4,1,""]},"rse_api.swagger.swagger_spec.OpenApiParameter":{remapped_fields:[9,4,1,""]},"rse_api.swagger.swagger_spec.OpenApiParameterInput":{COOKIE:[9,4,1,""],HEADER:[9,4,1,""],PATH:[9,4,1,""],QUERY:[9,4,1,""]},"rse_api.swagger.swagger_spec.OpenApiPath":{remapped_fields:[9,4,1,""]},"rse_api.swagger.swagger_spec.OpenApiPathOperation":{remapped_fields:[9,4,1,""],required_fields:[9,4,1,""]},"rse_api.swagger.swagger_spec.OpenApiReference":{remapped_fields:[9,4,1,""],to_component_type:[9,6,1,""],to_schema:[9,6,1,""]},"rse_api.swagger.swagger_spec.OpenApiSchema":{from_marshmallow:[9,6,1,""],get_type_map_for:[9,6,1,""],remapped_fields:[9,4,1,""],render:[9,3,1,""]},"rse_api.swagger.swagger_spec.OpenApiSecurityInputFrom":{COOKIE:[9,4,1,""],HEADER:[9,4,1,""],QUERY:[9,4,1,""]},"rse_api.swagger.swagger_spec.OpenApiSecurityType":{APIKEY:[9,4,1,""],HTTP:[9,4,1,""],OAUTH:[9,4,1,""],OPEN_ID_CONNECT:[9,4,1,""]},"rse_api.swagger.swagger_spec.OpenApiServer":{required_fields:[9,4,1,""]},"rse_api.swagger.swagger_spec.OpenApiServerVariable":{required_fields:[9,4,1,""]},"rse_api.swagger.swagger_spec.OpenApiStringFormats":{BINARY:[9,4,1,""],BYTE:[9,4,1,""],DATE:[9,4,1,""],DATETIME:[9,4,1,""],EMAIL:[9,4,1,""],HOSTNAME:[9,4,1,""],IPV4:[9,4,1,""],IPV6:[9,4,1,""],PASSWORD:[9,4,1,""],URI:[9,4,1,""]},"rse_api.swagger.swagger_spec.OpenApiTag":{remapped_fields:[9,4,1,""],required_fields:[9,4,1,""]},"rse_api.tasks":{app_context_middleware:[10,0,0,"-"],dramatiq_parse_arguments:[10,1,1,""]},"rse_api.tasks.app_context_middleware":{AppContextMiddleware:[10,2,1,""]},"rse_api.tasks.app_context_middleware.AppContextMiddleware":{after_process_message:[10,3,1,""],after_skip_message:[10,3,1,""],before_process_message:[10,3,1,""],state:[10,4,1,""]},"rse_api.utils":{dynamic_import_all:[7,1,1,""],load_modules:[7,1,1,""]},rse_api:{cli:[7,0,0,"-"],controllers:[8,0,0,"-"],decorators:[7,0,0,"-"],default_dramatiq_setup_broker:[7,1,1,""],default_dramatiq_setup_result_backend:[7,1,1,""],errors:[7,0,0,"-"],get_application:[7,1,1,""],get_restful_api:[7,1,1,""],get_worker_cli:[7,1,1,""],query:[7,0,0,"-"],run_cron_workers:[7,1,1,""],start_dramatiq_workers:[7,1,1,""],swagger:[9,0,0,"-"],tasks:[10,0,0,"-"],utils:[7,0,0,"-"]}},objnames:{"0":["py","module","Python module"],"1":["py","function","Python function"],"2":["py","class","Python class"],"3":["py","method","Python method"],"4":["py","attribute","Python attribute"],"5":["py","exception","Python exception"],"6":["py","classmethod","Python class method"]},objtypes:{"0":"py:module","1":"py:function","2":"py:class","3":"py:method","4":"py:attribute","5":"py:exception","6":"py:classmethod"},terms:{"400s":7,"boolean":9,"byte":9,"class":[7,8,9,10],"const":9,"default":[7,9],"enum":9,"final":9,"float":9,"function":[7,9],"import":[2,7,11],"int":[7,9],"new":7,"public":4,"return":[7,9,10],"throw":7,"true":[7,9],"while":2,And:7,For:[7,9],NOT:9,Not:9,The:[1,4,7,9],Then:1,Useful:7,__init__:[7,9],__tablename__:7,_local:10,_modul:7,_thread:10,abc:9,abl:7,about:1,abov:9,actor:[2,7],add:[1,2,7,9],add_class_request:9,add_class_respons:9,add_cli:7,add_marshmallow_schema:9,add_schema:9,added:7,addit:[7,9],additional_item:9,additional_properti:9,advanc:7,after:10,after_process_messag:10,after_skip_messag:10,all:[1,2,7],allof:9,allow:[2,7,9,10],allow_empti:9,allow_reserv:9,along:9,also:[7,9],alwai:[1,4,9],ani:[1,7,9],anoth:7,anyof:9,anyth:1,api:[6,7,9],api_licens:9,apikei:9,app:[7,9,10],app_context_middlewar:[5,7],app_vers:7,appcontextmiddlewar:10,appgroup:7,appli:[7,9],applic:[7,9],appreci:1,apschedul:7,arg:7,argument:[7,9],arrai:[7,9],articl:1,assum:[1,7,9],attach:7,attempt:7,authorization_cod:9,authorization_url:9,autodetect_http_cod:9,autoincr:7,automat:7,back:7,backend:[2,7],base:[7,8,9,10],basic:7,bearer_format:9,becaus:9,been:[9,10],befor:[7,10],before_process_messag:10,behav:2,behaviour:9,being:7,below:7,best:1,better:9,binari:9,bit:1,blob:9,block:7,blockingschedul:7,blog:1,bodi:7,bool:[7,9],both:7,branch:1,broker:[7,10],bug:2,bugfix:1,build:9,built:9,bumpvers:1,cach:7,calcul:9,call:[7,10],callabl:[7,9],callback:9,can:[1,4,7,9],cast:9,caution:9,certain:7,chanc:7,chang:1,check:1,checkout:1,classmethod:9,clearer:2,cli:[5,10],client:7,client_credenti:9,clone:[1,4],code:9,column:[7,8],com:[1,4,9],combin:9,combine_typ:9,command:[4,7,10],commit:[1,7],common:[6,7],compon:9,condit:7,conditional_decor:7,config:7,configur:7,connect:7,consolid:6,constructor:9,contact:9,contain:[7,9],content:[3,5],content_typ:9,contina:7,contribut:3,contributor:7,control:[5,7,9],convers:9,convert:[7,9],cooki:9,cookiecutt:1,copi:[1,4,9,10],cor:7,core:9,corn:7,could:1,creat:[1,7],createdandupdatedatmixin:7,credit:[1,3],cron:7,crontab:7,cross:7,cross_origin:7,curl:4,current:[7,10],current_app:7,data:[7,9],data_pattern:7,data_typ:9,date:9,datetim:9,debug:7,declar:9,decor:5,def:[7,9],default_dramatiq_setup_brok:7,default_dramatiq_setup_result_backend:7,default_error_handl:7,default_in_schema:7,defin:7,definit:[7,9],delet:[7,8,9],delete_by_pk:7,depend:9,deploi:3,deprec:9,descript:[1,7,9],dest_typ:9,detail:1,detect:[7,9],detect_mani:7,dev:7,develop:[1,7],dict:[7,9],dictionari:[7,9],dir_path:7,directori:7,disabl:7,doc:1,docstr:1,document:[2,6,7,9],doe:9,doing:7,don:4,done:1,doubl:9,download:4,dramatiq:[2,7,10],dramatiq_parse_argu:10,dramtiq:7,driven:1,dummp:9,dump:[7,9],dure:7,dynamic_import_al:7,each:7,earlier:2,easi:9,easier:1,either:[4,7,9],els:7,email:9,emit:10,enabl:7,encod:9,endpoint:7,enhanc:1,ensur:7,entri:1,enumer:9,env:7,environ:7,equival:7,error:[2,5],etc:9,even:1,everi:1,exampl:[7,9],except:[7,10],exclud:[7,9],exclude_on_post:8,excluded_field:9,exclusive_maximum:9,exclusive_minimum:9,exist:9,exit:7,expect:[7,9],explain:1,explod:9,express:9,external_doc:9,external_valu:9,extra_exclud:9,fail:7,fals:[7,9],featur:[3,7],field:[7,9],file:[1,7,9],filter:7,fimctopm:7,find:7,find_al:8,find_on:[7,8],find_rule_by_url:9,find_view_func_by_url:9,first:[2,9],fix:2,flake8:1,flask:[7,8,9],flask_rest:[2,7],flow:9,folder:7,follow:7,fork:1,format:9,from:[3,7,9,10],from_marshmallow:9,from_marshmallow_opt:9,func:7,gener:[7,9],generate_swagg:7,get:[3,7,8,9],get_appl:[2,7],get_db:7,get_declarative_bas:7,get_pagination_from_request:7,get_restful_api:7,get_swagger_config:7,get_swagger_registri:[7,9],get_type_map_for:9,get_worker_cli:7,git:[1,4],github:[1,4,6,9],given:1,global:9,greatli:1,group:7,guid:4,guru:7,handler:7,has:[7,10],have:[1,4,7,9],head:9,header:9,help:1,here:[1,7],highlight:7,histori:[1,3],host:[2,7],hostnam:9,how:1,html:[7,9],http:[1,4,6,7,9],idmixin:7,ignor:9,ignorenoneitermixin:9,implicit:9,improv:2,in_loader_func:7,includ:[1,2,7,9],index:3,info:9,input:7,input_from:9,instal:[1,3],instanc:7,instance_loader_func:7,instead:10,institutefordiseasemodel:[1,4,6],int32:9,int64:9,integ:9,ipv4:9,ipv6:9,issu:[1,2],item:[7,9],item_nam:9,iter:9,its:7,ize:9,json:[7,9],json_onli:7,just:[1,7],keep:1,kei:7,kwarg:[7,9],last:9,lastli:9,later:7,latest:[7,9],len:7,librari:6,like:9,link:9,list:[7,8,9],listen:7,littl:1,load:7,load_modul:7,local:1,logger:7,look:1,loop:7,mainli:7,maintain:1,major:1,make:[1,2,7],manag:7,mani:[1,7],many_schema:8,map:9,marshmallow:[2,7,9],marshmallow_schema:9,marshmallow_sqlalchemi:7,master:[4,9],match:[7,9],max_item:9,max_length:9,max_properti:9,maximum:9,mean:7,meant:6,merg:7,messag:[2,7,10],meta:7,method:[4,7,8,9],method_nam:9,methodview:8,middlewar:10,might:1,min_item:9,min_length:9,min_properti:9,minimum:9,minor:1,minu:7,miss:7,mkvirtualenv:1,mode:7,model:[7,8],modelschema:7,modul:[3,5],more:1,most:4,move:2,multiple_of:9,must:9,name:[1,7,9],narrow:1,need:[7,9],nested_convert:9,next:9,none:[7,8,9,10],noresultfound:7,note:7,now:1,nullabl:7,number:[7,9],oai:9,oauth2:9,oauth:9,object:[7,9,10],offici:1,onc:4,one:7,oneof:9,onli:[7,9],onto:9,ontof:9,opanapischemacombinetyp:9,open:[1,9],open_api_operation_prop:7,open_id_connect:9,open_id_connect_url:9,openapi:[7,9],openapi_:7,openapi_operation_prop:9,openapi_request:9,openapi_respons:9,openapicallback:9,openapicompon:9,openapicontact:9,openapidatatyp:9,openapidocu:9,openapiencod:9,openapiexampl:9,openapiexternaldocument:9,openapihead:9,openapiinfo:9,openapiintformat:9,openapilicens:9,openapilink:9,openapimediatyp:9,openapimethod:9,openapinumberformat:9,openapioauthflow:9,openapioper:9,openapiparamet:9,openapiparameterinput:9,openapipath:9,openapipathoper:[7,9],openapirefer:9,openapiregistri:9,openapirequestbodi:9,openapirespons:9,openapischema:9,openapischemacombin:9,openapisecur:9,openapisecurityinputfrom:9,openapisecuritytyp:9,openapiserv:9,openapiservervari:9,openapistringformat:9,openapitag:9,openidconnect:9,openmediatyp:9,oper:[1,7,9],operation_id:9,operation_ref:9,option:[7,9],order_bi:8,org:9,origin:[1,7],other:1,otherwis:7,our:[7,9,10],out:7,out_format:9,output:[7,9],over:9,packag:[2,3,5],package_path:7,page:[3,7],page_default:7,pagin:7,param:[7,9],paramet:[7,9],parameters_from_url:9,pars:[7,9],part:[1,7,9],partial:7,pass:[1,7,9],password:9,patch:[1,9],path:[7,9],pattern:9,per:7,per_pag:7,per_page_default:7,perpag:7,pika:7,pip:[1,4],pleas:1,possibl:[1,7],post:[1,7,8,9],practic:6,prefer:[4,9],prefix:7,present:7,print:7,process:[2,4,10],project:[1,7,11],project_nam:1,prop:9,properti:9,propos:1,proprerti:9,provid:[7,9],pull:1,push:1,put:[7,8,9],pypi:1,python:[1,4,7],queri:[5,9],quickli:6,quickstart:7,rabbit:7,rabbitmq:7,rais:[7,10],readi:[1,7],readthedoc:7,recent:4,recommend:7,redi:7,redis_uri:7,redisbackend:7,reduc:7,refer:9,refresh_url:9,reg:7,regist:7,register_common_error_handl:7,register_controller_resourc:9,register_resourc:[7,9],registri:9,releas:[2,3],remap:9,remapped_field:9,rememb:1,remind:1,render:9,repo:[1,4],repositori:4,repres:9,reproduc:1,request:[1,7,9],request_bodi:9,request_obj:9,requir:[7,9],required_field:9,required_properti:9,resourc:[2,7,9],respons:[7,9],response_obj:9,rest:[6,7],result:[2,7,10],rfc:9,rout:7,rse:6,rse_api:[1,2,4,11],rse_db:7,rseapiexcept:7,rsebasicreadwritemodel:7,rst:1,run:[1,4,7],run_cron_work:7,runtim:7,save:7,scan:7,schedul:7,schema:[7,8,9],schema_in:7,schema_in_loader_func:7,schema_in_mani:7,schema_in_out:7,schema_in_parti:7,schema_out:7,schema_out_detect_mani:7,schema_out_mani:7,schemain:7,schemaout:7,schena:7,scope:[1,9],search:3,section:9,secur:9,security_schem:9,security_typ:9,see:[0,7,9],self:[7,9],send:1,serial:7,server:9,servic:6,session:7,set:[1,2,7,9],setting_environment_vari:7,setting_object_path:7,setup:[0,1,2,4,7],setup_broker_func:7,setup_results_backend_func:7,should:[7,9,10],show:7,show_rout:7,simple_control:[5,7],simplecontrol:8,sinc:7,singl:7,single_schema:8,singleton:7,singleton_funct:7,skip:10,skipmessag:10,slash:7,sm_in_schema:7,sm_out_schema:7,smart:7,smartusercontrol:7,smartuserschema:7,some:[7,9],sourc:[3,7,8,9,10],specif:[7,9],specifi:[7,9],sql:8,sqla_sess:7,sqlalchemi:8,stabl:3,stand:6,start:[3,7],start_dramatiq_work:7,state:10,statu:9,status_cod:9,step:1,still:2,store:7,str:[7,8,9],strict:7,strict_slash:7,string:[7,9],stub:7,style:9,subfold:2,submodul:5,subpackag:5,subset:1,succe:7,summari:9,suppli:7,support:[2,7,9],sure:1,swagger:[5,7],swagger_control:[5,7],swagger_cor:7,swagger_registri:[5,7],swagger_spec:[5,7],swaggerspecformat:9,system:1,tag:[1,9],take:7,tarbal:4,target_class:9,task:[5,7],tasktag:7,team:6,templat:7,template_fold:7,termin:4,terms_of_servic:9,test:[1,7],test_rse_api:1,text:7,textio:9,thank:7,thei:1,them:1,thi:[1,4,7,9,10],those:[7,9],three:9,through:[1,4,7],time:[7,9],timeit_log:7,timestamp:7,tip:3,titl:9,to_component_typ:9,to_schema:9,to_typ:9,todo:6,token_url:9,too:7,tox:1,trace:9,track:7,travi:1,trigger:7,troubleshoot:1,tupl:9,turn:7,type:[3,7,9],understand:9,union:[7,8,9],unique_item:9,updat:[7,9],update_class_method_prop:9,uri:9,url:[2,7,9],usag:3,use:[1,7,10,11],used:[7,9],useful:7,user:[7,9],usercontrol:[7,9],usermodel:7,usernam:7,userresourc:7,userschema:[7,9],uses:7,using:[7,9],usual:7,util:5,valid:[7,9],valu:[7,9],vanilla:7,variabl:[7,9],version:[1,7,9],view:[8,9],virtualenv:1,virtualenvwrapp:1,volunt:1,wai:[1,9],want:[1,9],web:1,websit:1,welcom:1,were:7,what:7,when:[1,7,9,10],whether:[1,7],which:[7,9],whoever:1,within:[6,10],without:9,word:[7,9],work:1,worker:7,would:[1,9],wrap:[7,9],wrapper:[2,7],write:[7,9],yaml:9,you:[1,4,7,9],your:[1,4],your_name_her:1},titles:["Credits","Contributing","History","Welcome to rse_api\u2019s documentation!","Installation","rse_api","rse_api","rse_api package","rse_api.controllers package","rse_api.swagger package","rse_api.tasks package","Usage"],titleterms:{app_context_middlewar:10,bug:1,cli:7,content:[7,8,9,10],contribut:1,control:8,credit:[0,6],decor:[7,9],deploi:1,document:[1,3],error:7,featur:[1,6],feedback:1,fix:1,from:4,get:1,histori:2,implement:1,indic:3,instal:4,modul:[7,8,9,10],packag:[7,8,9,10],queri:7,releas:4,report:1,rse_api:[3,5,6,7,8,9,10],simple_control:8,sourc:4,stabl:4,start:1,submit:1,submodul:[7,8,9,10],subpackag:7,swagger:9,swagger_control:9,swagger_registri:9,swagger_spec:9,tabl:3,task:10,tip:1,type:1,usag:11,util:7,welcom:3,write:1}})