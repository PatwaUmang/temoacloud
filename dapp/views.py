#Django
from django.template import RequestContext
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django import forms
from django.views.decorators.csrf import csrf_exempt

#System
import json
import os
import re
import urllib
import json
import os

#Custom / Thirdparty
from thirdparty import test
from thirdparty.temoa.db_io import Make_Graphviz
from handle_modelrun import run_model


def login(request):
  return render_to_response('login.html', context_instance=RequestContext(request))

def inputData(request):
  return render_to_response('InputData.html', { 'mode' : 'input'}, context_instance=RequestContext(request))

def outputData(request):
  return render_to_response('InputData.html', { 'mode' : 'output'}, context_instance=RequestContext(request))

def modelRun(request):
  return render_to_response('ModelRun.html', context_instance=RequestContext(request))

def runModel(request):
  
  msg = 'Successfully generated'
  result = True
  try:
    #This function will handle 
    #TODO try catch handling
    run_model(request)
  
  
  except:
    msg = 'An error occured.'
    result = False
  
  
  return JsonResponse( {"result" : result , "message" : msg  } )


def index(request):
  
  return HttpResponse("Nothing for now...")


def about(request):
  return render_to_response('About-Us.html', context_instance=RequestContext(request))

#@csrf_exempt
#def fileUpload(request):
#  upload_file(request)
#  return HttpResponse("File uploaded result")


#get posted data
def runInput(request):
  
  import uuid; 
  
  if request.method == 'POST':
    format = request.POST.get("format", "svg")
    colorscheme = request.POST.get("colorscheme", "color")
    commodityoutputlimit =request.POST.get("commodityoutputlimit", "")
    commodityinputlimit =request.POST.get("commodityinputlimit", "")
    filename =request.POST.get("datafile", "")
    mode =request.POST.get("mode", "")
    
    filename2, file_extension = os.path.splitext(filename)
    random = str(uuid.uuid4().get_hex().upper()[0:6])
    
    #fulldirpath = os.path.dirname(os.path.abspath(__file__))
    
    #print settings.BASE_DIR
    
    #filename = "/home/yash/Projects/dapp/thirdparty/temoa/db_io/temoa_utopia.sqlite"
    
    inputs = { 
            "-i" : settings.BASE_DIR + "/uploads/" + mode + "/" + filename , 
            "-f" : format,
            "--scenario" : random ,
            "-o" : settings.BASE_DIR + "/result/" + mode
          }
          
    if( colorscheme == "grey"):
      inputs['-g'] = colorscheme
    
    print inputs
    
    makeGraph(inputs)
    
    return JsonResponse( {"filename" : filename2 + "_" + random , "mode" : mode , } )
    
    
  

# Create your views here.
def makeGraph(inputs):
  #print test.tryme()
  
  #So we have to pass inputs to Make_Graphviz to generate graph
  #After getting response run a ajax call to get that
  
  
  
  
  
  Make_Graphviz.createGraphBasedOnInput(inputs)
  
  
  #expected result
  # image svg now fetch and show result
  #print "result/%s/" %( os.path.splitext(os.path.basename(filename))[0] )
  
  
  
  
  #if opt in ("-i", "input"):
    #ifile = arg
  #elif opt in ("-f", "--format"):
    #graph_format = arg
  #elif opt in ("-c", "--show_capacity"):
    #show_capacity = True
  #elif opt in ("-v", "--splinevar") :
    #splinevar = True
  #elif opt in ("-t", "--graph_type") :
    #graph_type = arg
  #elif opt in ("-s", "--scenario") :
    #scenario = arg
  #elif opt in ("-n", "--name") :
    #quick_name = arg
  #elif opt in ("-o", "--output") :
    #res_dir = arg
  #elif opt in ("-g", "--grey") :
  
  
  
  return HttpResponse("Index SSS") 


@csrf_exempt
def fileUpload(request):
    
  if request.method == 'POST':
    mode = request.POST.get("mode", "input")
    
    
    

    result = handle_uploaded_file( request.FILES['file'],  mode)
    
    #if string is empty we have no errors hence success
    if not result :
      #fileList = loadFiles()
      #JsonResponse( {'success' : 'File uploading finished'} )

      return JsonResponse( {"data" : loadFiles(mode) })
      
    
    return JsonResponse({'error': result}, status = 403)

def handle_uploaded_file(f, mode):
  import os.path
  
  
  fname = settings.BASE_DIR + '/uploads/'+mode+'/' + f.name
  
  
  filename, file_extension = os.path.splitext(f.name)
  print(fname)
  print file_extension
  
  if file_extension != ".data" and file_extension != ".sqlite" :
    return "Please select a valid file. Supported files are data and sqlite"
     
  
  if(os.path.isfile(fname) ):
    print "Testing" + fname
    return "File already exists. Please rename and try to upload."
  
  with open(fname, 'wb+') as destination:
    for chunk in f.chunks():
      destination.write(chunk)
  
  return "";


def loadFileList(request):
  mode = request.GET.get('mode','input')
  fileList = { "data" : loadFiles(mode) }
  return JsonResponse(fileList)

def loadFiles(mode):
  print mode
  #import glob   
  #print glob.glob("upload/adam/*.txt")
  types = ('.data', '.sqlite') # the tuple of file types
  
  return [each for each in os.listdir(settings.BASE_DIR + '/uploads/'+ mode) if each.endswith(types)]
  
  #files_grabbed = []
  #for type in types:
      ##files_grabbed.extend(glob.glob('uploads/'+ mode +'/' + type))
      #files_grabbed = [each for each in os.listdir('uploads/'+ mode) if each.endswith('.c')]
  #fileList = []

  #print files_grabbed

  #for file in files_grabbed:
    #fileList.append(os.path.basename(file))

  #print fileList

  #return fileList;

def loadCTList(request):
  mode = request.GET.get('mode','input')
  fileName = request.GET.get('filename')
  listType = request.GET.get('type','commodity')

  if listType == 'commodity':
    ctList = { "data" : {"0":"COAL",
                           "1": "METAL",
                           "2":"SOIL"}}

  if listType == 'technology':
    ctList = { "data" : {"0":"ELEC",
                           "1": "AIR",
                           "2":"FIRE"}} 

  return JsonResponse(ctList)

    

