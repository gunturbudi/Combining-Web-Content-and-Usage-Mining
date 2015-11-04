<!DOCTYPE html>
<!--[if lt IE 7]>      <html class="no-js lt-ie9 lt-ie8 lt-ie7"> <![endif]-->
<!--[if IE 7]>         <html class="no-js lt-ie9 lt-ie8"> <![endif]-->
<!--[if IE 8]>         <html class="no-js lt-ie9"> <![endif]-->
<!--[if gt IE 8]><!--> <html class="no-js"> <!--<![endif]-->
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
        <title>Framework Web Content dan Usage Mining</title>
        <meta name="description" content="">
        <meta name="viewport" content="width=device-width">
        <link rel="stylesheet" href="{{ get_url('static', path='bootstrap-3.3.4-dist/css/bootstrap.min.css') }}">
        <link rel="stylesheet" href="{{ get_url('static', path='normalize.css') }}">
        <link rel="stylesheet" href="{{ get_url('static', path='main.css') }}">
        <link rel="stylesheet" href="{{ get_url('static', path='jquery.steps.css') }}">
        <script src="{{ get_url('static', path='modernizr-2.6.2.min.js') }}"></script>
        <script src="{{ get_url('static', path='jquery-1.9.1.min.js') }}"></script>
        <script src="{{ get_url('static', path='bootstrap-3.3.4-dist/js/bootstrap.min.js') }}"></script>
        <script src="{{ get_url('static', path='jquery.cookie-1.3.1.js') }}"></script>
        <script src="{{ get_url('static', path='jquery.steps.min.js') }}"></script>
        <script src="{{ get_url('static', path='jquery.form.min.js') }}"></script>
        
        <style>
        	.content{display:block;min-height:35em;overflow-y: auto;position:relative}
        	.progress { position:relative; width:400px; border: 1px solid #ddd; padding: 1px; border-radius: 3px; }
			.bar { background-color: #B4F5B4; width:0%; height:20px; border-radius: 3px; }
			.percent { position:absolute; display:inline-block; top:3px; left:48%; }
        </style>
    </head>
    <body>
        <!--[if lt IE 7]>
            <p class="chromeframe">You are using an <strong>outdated</strong> browser. Please <a href="http://browsehappy.com/">upgrade your browser</a> or <a href="http://www.google.com/chromeframe/?redirect=true">activate Google Chrome Frame</a> to improve your experience.</p>
        <![endif]-->
        <div class="content">
        	
            <h1 style="margin-left:15px">Kombinasi  Web Usage dan Content Mining untuk Profil Navigasi Website</h1>
			
            <script>
                $(function ()
                {
                    $("#wizard").steps({
                        headerTag: "h2",
                        bodyTag: "section",
                        transitionEffect: "slideLeft",
                        stepsOrientation: "vertical"
                    });
                    $("#check_count_content").click(function(){
                    	$("#content_count_result").html('<img src="{{ get_url('static', path='loading.gif') }}" title="loading">')
                    	$.get( "/check_article", function( data ) {
							$( "#content_count_result" ).html( data );
						}) 
						.fail(function() {
							$( "#content_count_result" ).html( "Process Failed!" );
						});
						setAutoOverflow();
                    });
                    
                    $("#check_process_content").click(function(){
                    	$("#content_process_result").html('<img src="{{ get_url('static', path='loading.gif') }}" title="loading">')
                    	$.get( "/clean_article", function( data ) {
							$( "#content_process_result" ).html( data );
						}).fail(function() {
							$( "#content_process_result" ).html( "Process Failed!" );
						});
						setAutoOverflow();
                    });
                    
                    $("#check_status_content").click(function(){
                    	$("#content_status_result").html('<img src="{{ get_url('static', path='loading.gif') }}" title="loading">')
                    	$.get( "/status_cleaned_article", function( data ) {
							$( "#content_status_result" ).html( data );
						}) 
						.fail(function() {
							$( "#content_status_result" ).html( "Process Failed!" );
						});
						setAutoOverflow();
                    });

                    $("#create_corpus").click(function(){
                    	$("#corpus_status").html('<img src="{{ get_url('static', path='loading.gif') }}" title="loading">')
                    	var number_topic = $('#number_topic').val();
                    	$.get( "/create_corpus/"+number_topic, function( data ) {
							$( "#corpus_status" ).html( data );
						}) 
						.fail(function() {
							$( "#corpus_status" ).html( "Process Failed!" );
						});
						setAutoOverflow();
                    });

                    $("#see_model").click(function(){
                    	$("#see_model_span").html('<img src="{{ get_url('static', path='loading.gif') }}" title="loading">')
                    	var number_topic = $('#number_topic').val();
                    	var lang = $('#lang').val();
                    	$.get( "/see_model/"+number_topic+"/"+lang, function( data ) {
							$( "#see_model_span" ).html( data );
						}) 
						.fail(function() {
							$( "#see_model_span" ).html( "Process Failed!" );
						});
						setAutoOverflow();
                    });

                    $("#assign_topic").click(function(){
         	           	$("#assign_status").html('<img src="{{ get_url('static', path='loading.gif') }}" title="loading">')
                    	$.get( "/assign_topic", function( data ) {
							$( "#assign_status" ).html( data );
						}) 
						.fail(function() {
							$( "#assign_status" ).html( "Process Failed!" );
						});
						setAutoOverflow();
                    });
                    
                    $("#log_check").click(function(){
                    	$("#log_check_status").html('<img src="{{ get_url('static', path='loading.gif') }}" title="loading">')
                    	$.get( "/log_check", function( data ) {
							$( "#log_check_status" ).html( data );
						}) 
						.fail(function() {
							$( "#log_check_status" ).html( "Log File Not Valid or Not Exists" );
						});
						setAutoOverflow();
                    });
                    
                    $("#log_process").click(function(){
                    	$("#log_process_status").html('<img src="{{ get_url('static', path='loading.gif') }}" title="loading">')
                    	$.get( "/sessionization", function( data ) {
							$( "#log_process_status" ).html( data );
						}) 
						.fail(function() {
							$( "#log_process_status" ).html( "Process Failed!" );
						});
						setAutoOverflow();
                    });
                    
                    $("#train_som").click(function(){
                    	$("#train_som_status").html('<img src="{{ get_url('static', path='loading.gif') }}" title="loading">')
                    	$.get( "/train_som", function( data ) {
							$( "#train_som_status" ).html( data );
						}) 
						.fail(function() {
							$( "#train_som_status" ).html( "Process Failed!" );
						});
						setAutoOverflow();
                    });
                    
                    $("#test_som").click(function(){
                    	$("#test_som_status").html('<img src="{{ get_url('static', path='loading.gif') }}" title="loading">')
                    	$.get( "/test_som", function( data ) {
							$( "#test_som_status" ).html( data );
						}) 
						.fail(function() {
							$( "#test_som_status" ).html( "Process Failed!" );
						});
						setAutoOverflow();
                    });
                    
                    $("#see_som_map").click(function(){
                    	$("#see_som_map_status").html('<img src="{{ get_url('static', path='loading.gif') }}" title="loading">')
                    	var no_uji = $("#data_uji_som").val()
                    	$.get( "/see_som_map/"+no_uji, function( data ) {
							$( "#see_som_map_status" ).html( data );
						}) 
						.fail(function() {
							$( "#see_som_map_status" ).html( "Process Failed!" );
						});
						setAutoOverflow();
                    });
                    
                    $("#see_prefix_result").click(function(){
                    	$("#see_prefix_result_status").html('<img src="{{ get_url('static', path='loading.gif') }}" title="loading">')
                    	var no_uji = $("#data_uji_prefix").val()
                    	$.get( "/see_prefix_result/"+no_uji, function( data ) {
							$( "#see_prefix_result_status" ).html( data );
						}) 
						.fail(function() {
							$( "#see_prefix_result_status" ).html( "Process Failed!" );
						});
						setAutoOverflow();
                    });
                    
                    $("#prefixspan").click(function(){
                    	$("#prefixspan_status").html('<img src="{{ get_url('static', path='loading.gif') }}" title="loading">')
                    	
                    	$.get( "/prefixspan", function( data ) {
							$( "#prefixspan_status" ).html( data );
						}) 
						.fail(function() {
							$( "#prefixspan_status" ).html( "Process Failed!" );
						});
						setAutoOverflow();
                    });

                    $("#test_random_article").click(function(){
                    	$("#accordion_article").html('<img src="{{ get_url('static', path='loading.gif') }}" title="loading">')
                    	$("#accordion_recommendation").html("")
                    	$.get( "/test_random_article", function( data ) {
							$( "#accordion_article" ).html( data );
							$("#test_recommendation").show();
						}) 
						.fail(function() {
							$( "#accordion_article" ).html( "Process Failed!" );
						});
						setAutoOverflow();
                    });

                    $("#test_recommendation").click(function(){
                    	$("#accordion_recommendation").html('<img src="{{ get_url('static', path='loading.gif') }}" title="loading">')
                    	
                    	$.get( "/test_recommendation", function( data ) {
							$( "#accordion_recommendation" ).html( data );
							$("#explain_recommendation").show();
							$(".btn-rekomen").click(function(){
								$("#explain_recommendation").hide();

		                    	$("#accordion_recommendation").html('')
		                    	$("#accordion_article").html('<img src="{{ get_url('static', path='loading.gif') }}" title="loading">')
		                    	article_id = $(this).attr("id")
		                    	$.get( "/get_next_read/"+article_id, function( data ) {
									$( "#accordion_article" ).html( data );
								}) 
								.fail(function() {
									$( "#accordion_article" ).html( "Process Failed!" );
								});
								setAutoOverflow();
		                    });
						}) 
						.fail(function() {
							$( "#accordion_recommendation" ).html( "Process Failed!" );
						});
						setAutoOverflow();
                    });

                    
                    
                    
                    var bar = $('.bar');
					var percent = $('.percent');
					var status = $('#status');
                    $('#form_upload_log').ajaxForm({ 
                    	beforeSend: function() {
					        status.empty();
					        var percentVal = '0%';
					        bar.width(percentVal)
					        percent.html(percentVal);
					    },
					    uploadProgress: function(event, position, total, percentComplete) {
					        var percentVal = percentComplete + '%';
					        bar.width(percentVal)
					        percent.html(percentVal);
					    },
					    success: function() {
					        var percentVal = '100%';
					        bar.width(percentVal)
					        percent.html(percentVal);
					    },
						complete: function(xhr) {
							status.html(xhr.responseText);
							$('#form_upload_log').resetForm();
						}
	            	}); 
                });
                
                function setAutoOverflow(){
                	$('.content').css({"display":"block","min-height":"35em","overflow-y": "auto","position":"relative"});
                }
                
                function getPrefix(cluster,no_uji){
                	$('#modalArtikel').modal('toggle')
                	$('#modalArtikel').modal('show')
                	$("#article_container").html('<img src="{{ get_url('static', path='loading.gif') }}" title="loading">');
                	$("#myModalLabel").html("Sequence Result from Cluster " + cluster)
                	$.get( "/get_prefix_result/"+cluster+"/"+no_uji, function( data ) {
						$( "#article_container" ).html( data );
					})
					.fail(function() {
						$( "#article_container" ).html( "Process Failed!" );
					})					
                }
                
                function getSomResult(cluster,no_uji){
                	$('#modalArtikel').modal('toggle')
                	$('#modalArtikel').modal('show')
                	$("#article_container").html('<img src="{{ get_url('static', path='loading.gif') }}" title="loading">');
                	$("#myModalLabel").html("Session Topic from Cluster "+cluster)
                	$.get( "/get_som_result/"+cluster+"/"+no_uji, function( data ) {
						$( "#article_container" ).html( data );
					})
					.fail(function() {
						$( "#article_container" ).html( "Process Failed!" );
					})
                }
                
                function showArticle(topic){
                	$('#modalArtikel').modal('toggle')
                	$('#modalArtikel').modal('show')
                	$("#article_container").html('<img src="{{ get_url('static', path='loading.gif') }}" title="loading">');
                	str_topic = topic
                	if($("#lang").val()=="id") str_topic = parseInt(topic)+1
                	
                	$("#myModalLabel").html("Article from Topic "+str_topic)
                	$.get( "/get_article/"+topic, function( data ) {
						$( "#article_container" ).html( data );
					})
					.fail(function() {
						$( "#article_container" ).html( "Process Failed!" );
					});
                }
                
                function showWordCloud(topic){
                	$('#modalWordCloud').modal('toggle')
                	$('#modalWordCloud').modal('show')
                	$("#word_cloud_container").html('<img src="{{ get_url('static', path='loading.gif') }}" title="loading">');
                	str_topic = topic
                	if($("#lang").val()=="id") str_topic = parseInt(topic)+1
                	
                	$("#titleModalCloud").html("Visualisasi Topic "+str_topic)
                	$.get( "/get_wordcloud_visualisasi/"+topic, function( data ) {
						$( "#word_cloud_container" ).html( data );
					})
					.fail(function() {
						$( "#word_cloud_container" ).html( "Process Failed!" );
					});
                }
                
                function nextArticle(topic){
                	$("#article_container").html('<img src="{{ get_url('static', path='loading.gif') }}" title="loading">');
                	$.get( "/get_article/"+topic, function( data ) {
						$( "#article_container" ).html( data );
					})
					.fail(function() {
						$( "#article_container" ).html( "Process Failed!" );
					});
                }

                function explainRekomendasi(){
                	$("#accordion_recommendation").html('<img src="{{ get_url('static', path='loading.gif') }}" title="loading">')
                    	
                	$.get( "/explain_recommendation", function( data ) {
						$( "#accordion_recommendation" ).html( data );						
					}) 
					.fail(function() {
						$( "#accordion_recommendation" ).html( "Process Failed!" );
					});
					setAutoOverflow();
                }

            </script>
			<div class="modal fade" id="modalArtikel" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
			  <div class="modal-dialog">
			    <div class="modal-content">
			      <div class="modal-header">
			        <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
			        <h4 class="modal-title" id="myModalLabel">Data</h4>
			      </div>
			      <div class="modal-body" id="article_container">
			        ...
			      </div>
			      <div class="modal-footer">
			        <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
			      </div>
			    </div>
			  </div>
			</div>
			<div class="modal fade" id="modalWordCloud" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
			  <div class="modal-dialog modal-lg">
			    <div class="modal-content">
			      <div class="modal-header">
			        <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
			        <h4 class="modal-title" id="titleModalCloud">Visualisasi</h4>
			      </div>
			      <div class="modal-body" id="word_cloud_container">
			        ...
			      </div>
			      <div class="modal-footer">
			        <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
			      </div>
			    </div>
			  </div>
			</div>
			
            <div id="wizard">
                <h2>Content Acquisition</h2>
                <section>
                    <p>
                    	<h2>Scraping Steps</h2>
	                    <ul>
	                    	<li>Use Any Scraper tools that you want (for example: Scrapy, BeautifulSoup)</li>
	                    	<li>Put the scraped article in MongoDB collections (name of collection according to the settings.py)</li>
	                    	<li>Provide <strong>url</strong> column and <strong>article_html</strong> column into the collections</li>
	                    </ul>
	                    <!--
	                    <h2>Check Scraped Article</h2>
	                    <p><button id="check_count_content" type="button" value="Cek">Check</button></p>
                    	<p><span id="content_count_result"></span></p>
                    	
                    	<h2>Process Scraped Article</h2>
                    	<p><button id="check_process_content" type="button" value="Cek">Clean</button></p>
                    	<p><span id="content_process_result"></span></p>
                    	-->
                    	<h2>Check Article</h2>
                    	<p><button id="check_status_content" type="button" class="btn btn-primary" value="Cek">Check</button></p>
                    	<p><span id="content_status_result"></span></p>
                    </p>
                </section>

                <h2>Topic Modelling</h2>
                <section>
                    <h2>
                    	Topic Modelling with Latent Dirichlet Allocation
                    </h2>
                    <p>
                    	<input type="text" value="10" id="number_topic" name="number_topic" /><br/>
                    	<button class="btn btn-primary" id="create_corpus" type="button" value="Create">Create</button>
                    </p>
                    <p><span id="corpus_status"></span></p>
                    <h2>
                    	Assign Topic To Article
                    </h2>
                    <p><button class="btn btn-primary" id="assign_topic" type="button" value="Assign">Assign</button></p>
                    <p><span id="assign_status"></span></p>
                    <h2>
                    	Print Model
                    </h2>
                    <p>
                    	<select id="lang">
                    		<option value="id">Indonesian</option>
                    		<option value="en">English</option>
                    	</select>
                    </p>
                    <p><button class="btn btn-primary" id="see_model" type="button" value="Create">See Model</button></p>
                    <p><span id="see_model_span"></span></p>
                    
                    
                    
                </section>

                <h2>Log Acquisition</h2>
                <section>
                    <form action="/upload_log" method="post" id="form_upload_log" enctype="multipart/form-data">
			  				Select a log file: <input type="file" name="upload" />
			  				<input type="submit" value="Start upload" />
					</form>

					<div class="progress">
				        <div class="bar"></div >
				        <div class="percent">0%</div >
				    </div>
				    <div id="status"></div>
				    
				    <h2>Validate Log File</h2>
				    <p><button id="log_check" class="btn btn-primary" type="button" value="Check">Check</button></p>
                    <p><span id="log_check_status"></span></p>
                </section>

                <h2>Integrasi Log dan Topic</h2>
                <section>
                    <h3>Sessionization and Topic Integrating</h3>
                    <p><button class="btn btn-primary" id="log_process" type="button" value="Process">Process</button></p>
                    <p><span id="log_process_status"></span></p>
                </section>
                
                <h2>Session Topic Clustering</h2>
                <section>
                    <h3>Train SOM</h3>
                    <p><button class="btn btn-primary" id="train_som" type="button" value="Train SOM">Train!</button></p>
                    <p><span id="train_som_status"></span></p>
                    <h3>Apply SOM</h3>
                    <p><button class="btn btn-primary" id="test_som" type="button" value="Test SOM">Apply!</button></p>
                    <p><span id="test_som_status"></span></p>
                    <h3>Show Result Map</h3>
                    <p><button class="btn btn-primary" id="see_som_map" type="button" value="Lihat Map">Show!</button></p>
                    <p><select id="data_uji_som"><option value="0">0</option><option value="1">1</option><option value="2">2</option><option value="3">3</option><option value="4">4</option></select>
                    <p><span id="see_som_map_status"></span></p>
                    
                    
                </section>
                
                <h2>Sequence Pattern Mining</h2>
                <section>
                    <h3>Sequential Pattern Mining dengan PrefixSpan</h3>
                    <p><button class="btn btn-primary" id="prefixspan" type="button" value="GoPrefix">Run!</button></p>
                    <p><span id="prefixspan_status"></span></p>
                    
                    <h3>Result</h3>
                    <p><button class="btn btn-primary" id="see_prefix_result" type="button" value="GoPrefix">See Result</button></p>
                    <p><select id="data_uji_prefix"><option value="0">0</option><option value="1">1</option><option value="2">2</option><option value="3">3</option><option value="4">4</option></select>
                    <p><span id="see_prefix_result_status"></span></p>
                </section>
                
                <h2>Testing Profile</h2>
                <section>
                	<p><button class="btn btn-primary" id="test_random_article" type="button" value="Random">Get Random Article!</button></p>

                	<p>
						<div class="panel-group" id="accordion_article" role="tablist" aria-multiselectable="true">
						  
						</div>
                	</p>

                	<p>
                	<button class="btn btn-primary" id="test_recommendation" style="display:none" type="button" value="Random">Get Recommendation!</button>
                	<button class="btn btn-success" onclick="explainRekomendasi()" id="explain_recommendation" style="display:none" type="button" value="Explain">Explain Recommendation!</button>
                	</p>
                	

                	<p>
                		<div class="panel-group" id="accordion_recommendation" role="tablist" aria-multiselectable="true">
						  
						</div>
                	</p>


                </section>
            </div>
        </div>
    </body>
</html>