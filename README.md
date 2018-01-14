# ChromeDinoBrains


<img src="https://raw.githubusercontent.com/GensaGames/ChromeDinoBrains/master/chrome_sample.gif" width="900" height="400" /> 


  Neural Network, which teaching Dino Jump. Inspired by another Chrome Dino Project and [Open AI Blog](https://blog.openai.com/evolution-strategies/). This is completely  new and clear Neural Network Project, which represent Finite Difference. Your can use local trained source, to check all results. 

  So far, we using custom Game Scanner to resolve data for the Agent. Instead of taking whole Image, which time consuming for quick Dino operations. Project requires some third party dependencies, for running it locally. 

### Dependencies 

  `Selenium` for running Web Browser and fetching Image. We using Firefox, which much more faster performing Key Events too. `Jsonpickle` for saving/retrieving information in readable format. `Open CV` to loading Image in most fast way and gray format. `Psutil` for prioritizing current process. 

  We also using local setting ro run Web Browser with custom HD Screen Resolution. See Game Scanner file for more information. You can configure work for any resolution, but in our case, we want to save performance as much, as it possible. 

### Installing
To install Project locally, make sure you set all dependencies above. Running configuration: -s (Path to the Project)\ChromeDinoBrain\temp\.FiniteLearner (Or leave it empty, for training new results) -p <Population Size>. You can also update other settings in the relevant file - Settings.py. 
