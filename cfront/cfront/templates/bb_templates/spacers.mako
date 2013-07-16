<script type="unknown" id="spacer-h-v-template">
  <table class="spacer-hits">

  </table>
</script>
<script type="unknown" id="hit-v-template">

</script>


<!-- A view for a single spacer element in Left Column-list view -->
<script type="unknown" id="spacer-list-v-template">
  <span class="header">Spacer <span class="rank-container">{{id}}</span></span><br/>
  <span class="position-container">position: 
    <span class="strand">{{strand == 1? "+" : "-"}}</span>
    <span class="position">{{position}}</span><br/>
  </span>
  <span class="guide" style="font-family:courier">{{guide}}</span> <span style="font-family:courier; color:blue" class="nrg">{{nrg}}</span></br/>
  <span class="score-container">score: <span class="score">{{score}}</span></span>
</script>

<!-- A view containing all spacers in the left column -->
<script type="unknown" id="job-s-v-template">
  <div class="good section">
    <p class="header">guides having very few off-target hits in the genome</p>
    <ul class="views">
    </ul>
  </div>
  <div class="bad section">
    <p class="header">guides with substantial off-target cutting in the genome</p>
    <ul class="views">
    </ul>
  </div>
  <div class="uncategorized section">
    <p class="header">guides not yet aligned to the genome</p>
    <ul class="views">
    </ul>
  </div>
</script>
