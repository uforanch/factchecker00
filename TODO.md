MAIN
 * Secondary branch 
   * Change to new kubes code (include manifests) DONE
   * Update the prompting DONE
   * test refactor and fix bugs, maybe merge all into refactor DONE
   * merge back into main
 
NEXT:
* refactor threadpool to asyncio gather
* Update the comments to be consistent across modules

AFTER THAT
* Get "bytecode" out
* Get all the typing in
* Switch to async
* Give scraper a backup call to archive.ph
* Create tests
  * Create insertion function for news api
  * Create further outlines for how to test current data
* Possible other idea - post Async - make even MORE async. Run finding the data on each article found immediately, and publish analysis for each article as soon as it's done