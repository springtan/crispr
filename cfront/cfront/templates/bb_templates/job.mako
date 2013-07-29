<script type="unknown" id="job-v-template">
  <div class="header showing-less">
    <!--header-->
    <h1>Optimized CRISPR Design</h1>
    <h4 style="display:inline;">For query sequence "{{name}}" </h4>
    <a class="show-more less med-left-margin annotation">... show info</a>
    <a class="med-left-margin more annotation show-less">... hide info?</a>
    <div class="job-description med-left-margin med-top-margin more">
      <dl>
	<dt>Submitted by:</dt><dd>{{email}}</dd><br/>
	<dt>Date submitted:</dt><dd>{{submitted}}</dd><br/>
	<dt>Date completed:</dt><dd>{{completed}}</dd><br/>
	<dt>Aligns to:</dt><dd>hg19 on the <b>{{strand=="1"?"sense":"antisense"}}</b> strand of <b>{{chr}}</b> at <b>{{start}}</b> ({{locus}})</dd><br/>
	<dt>Sequence:</dt><dd class="seq"><span class="break-all dna">{{seq_html}}</dna></dd><br/>
	<dt>Statistics:</dt><dd>{{sequence.length}}nt, contains {{spacers.length}} possible guide sequences</dd><br/>
      </dl>
    </div>

    <!-- status display area -->
    <div class="status">
      <div style="white-space:nowrap;">
	<control><input id="email-complete" class="inline v-middle" {{email_complete?"checked":""}} type="checkbox"></input><label class="med-left-margin unselectable inline v-middle" for="email-complete">email ({{email}}) on completion</label></control>
      </div>
      <div class="progress progress-striped active">
	<div class="bar" style="width: 0%;"></div>
      </div>
      <div style="white-space:nowrap;">
	STATUS: <span class="text">locating guides... should take a couple of seconds</span>
      </div>
    </div>
    
    <!-- files download area -->
    <div class="files-area"></div>
    
    <!-- svg drawing area -->
    <div class="header"><span class="section-name">Interactive results: </span><span class="annotation med-left-margin">mouse over a guide or explore below for details</div>
  </div>
  <div class="svg-container">
    <div class="selection-svg">
    </div>
  </div>
</script>

<script type="unknown" id="job-v-svg-container-template">
</script>


<!-- A view containing all spacers in the left column -->
<script type="unknown" id="job-s-v-template">
  <div class="header showing-less">
    <div><h4>all guides</h4></div>
    <div>scored by inverse likelihood of offtarget binding</div>
    <span class="annotation">mouse over for details</span> 
    <a class="med-left-margin less show-more annotation">... show legend</a>
    <a class="med-left-margin more show-less annotation">... hide legend</a>

    <div class="guide-quality more">
      <div class="high-quality color-text"> high quality guide</div>
      <div class="medium-quality color-text"> mid quality guide</div>
      <div class="low-quality color-text"> low quality guide</div>
    </div>
  </div>
  <table class="med-top-margin">
    <thead>
      <tr> 
	<th></th>
	<th class="center">score</th>
	<th class="center">sequence</th>
      </tr>
    </thead>
    <tbody class="views"></tbody>
  </table>
</script>
