 function populateFileList(str) {
    var url = '/loadfilelist';
    $.ajax({
        url: url,
        dataType: 'json',
        method: 'get',
        data: {
            mode: str
        },
        success: function(result) {
            
            var options = '<option value="0">--Select data File--</option>';
            $.each(result.data, function(index, obj) {
                options += "<option value=" + obj + ">" + obj + "</option>";
            });
            $("#"+str+"datafilename").html(options);
            
        }
    });
}

 
 function initDropZone(str){
    // Dropzone class:
    var myDropzone = new Dropzone("div#"+str+"dropArea", {
        url: "/fileupload",
        params: {
        mode: str
    }
    });

    myDropzone.on("success", function(fileList, response) 
    {
        
        var options = '<option value="0">--Select data File--</option>';
        
        $.each(response.data, function(index, obj) {
            options += fileList.name == obj ? "<option selected='selected' value=" + obj + ">" + obj + "</option>" :
                "<option value=" + obj + ">" + obj + "</option>";
        });
        
        //$("#"+str+"datafilename").html(options);
        
        //Update output in all cases
        $("#outputdatafilename").html(options);
        $("#inputdatafilename").html(options);
  
        //if(str == "input")
            
        if(str == "output")
        {
           outputBlank(false);
        }

        myDropzone.removeAllFiles();

    });

   } 

function initJs()
{ 
    populateFileList('input');
    populateFileList('output');
    initDropZone('input');
    initDropZone('output');
   
    initForm();
    
    $("input[name='runoption']").click(function() {

       //alert("clicked");
    
        selected_val =  $(this).val() ;
        //alert(selected_val)
    
        if( selected_val == "Single-Run")
        {
            $(".UncertaintyAnalysisOptions, .MGAConfiguration").addClass("hidden");
            //alert("hide")
        }
        else if (selected_val == "Uncertainty-Analysis")
        {
            $(".UncertaintyAnalysisOptions, .MGAConfiguration").removeClass("hidden");
            //alert("show")
        }
    
    

   });
   
   
   
}





function outputBlank(isBlank)
{
    
    if(isBlank)
    {
        $("input[name='createspreadsheetoption']").prop("disabled", true);
        $("input[name='createspreadsheetoption'][value='']").prop("checked",true);
        $("input[name='createtextfileoption']").prop("disabled", true);
        $("input[name='createtextfileoption'][value='yes']").prop("checked",true);
    }
    else
    {
        $("input[name='createspreadsheetoption']").prop("disabled", false);
        $("input[name='createspreadsheetoption'][value='yes']").prop("checked",true);
        $("input[name='createtextfileoption']").prop("disabled", false);
        $("input[name='createtextfileoption'][value='yes']").prop("checked",true);
    }
    
    
}

function initForm() { 


    outputBlank(true);
    showDownloadButtonWithHelp(false, 'output');
    showDownloadButtonWithHelp(false, 'input');

    $("#outputdatafilename").change(function(){

        if($(this).val() == 0 )
        {
            outputBlank(true);
            showDownloadButtonWithHelp(false, 'output', '');
        }
        else
        {
            outputBlank(false);
            showDownloadButtonWithHelp(true, 'output', $(this).val());
        }
              
    });
    

    $("#inputdatafilename").change(function(){

        if($(this).val() == 0 )
        {
            showDownloadButtonWithHelp(false, 'input', '');
        }
        else
        {
            showDownloadButtonWithHelp(true, 'input', $(this).val() );
        }
              
    });
    
    


    
    var url = '/model';
    
    
    
    $("#input-file-error").hide();
    $("#output-file-error").hide();
    $("#scenarioname-error").hide();
    $("#solver-error").hide();
	
    
    $("#model-run-form").submit(function(e) {
            
        e.preventDefault();
        
        var isErrors;
        
        var fileInput = $("#inputdatafilename option:selected").text();
        if (fileInput == '--Select data File--' || fileInput == '') 
        {
            $("#input-file-error").show();
            isErrors = true;
        } 
        else 
        {
            $("#input-file-error").hide();
        }

        /*var fileOutput = $("#outputdatafilename option:selected").text();
        if (fileOutput == '--Select data File--' || fileOutput == '') 
        {
            $("#output-file-error").show();
            isErrors = true;
        } 

        else 
        {
            $("#output-file-error").hide();
        }*/
        
        
        scenarioname = $("input[name='scenarioname']").val();
        if( scenarioname == '')
        {
            $("#scenarioname-error").show();
            isErrors = true;
        }
        else
        {
            $("#scenarioname-error").hide();
        }
        
        solver = $("input[name='solver']").val();
        if( solver == '')
        {
            $("#solver-error").show();
            isErrors = true;
        }
        else
        {
            $("#solver-error").hide();
        }
        
        if(isErrors)
            return false;
            
       $(".spinner").removeClass("invisible");     
        
        
        $.post( url, $('form#model-run-form').serialize(), function(data) {
            
            
            //alert(data.message);

            $("#outputarea").val(data.output);
            
             //Make download button ready
			   $(".spinner").addClass("invisible");
            
            if(data.zip_path != "")
                $("#download-button").addClass("btn-yellow").attr("href", "/static/" + data.zip_path);
            
        },
       'json' // I expect a JSON response
    );
});
}


function showDownloadButtonWithHelp(isShow, mode, datafilename)
{
    if(isShow)
    {
        $("#download-"+mode+"-db").removeClass('hidden');
        $("#download-"+mode+"-button-help").removeClass('hidden');
        
        $("#download-"+mode+"-db").attr("href", "/static/uploaded/files/" + datafilename );
        
    }
    else
    {
        $("#download-"+mode+"-db").addClass('hidden');
        $("#download-"+mode+"-button-help").addClass('hidden');
    }
}
