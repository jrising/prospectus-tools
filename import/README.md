# DMAS Upload Tool for R

To install,

```
install.packages("devtools")
library(devtools)
install_github("jrising/prospectus-tools", subdir="import/rdmas")
```

# Adding R models to DMAS

The remainder of this document walks you through how to import a model from R to the Distributed Meta-Analysis System (DMAS).

## Basic Setup

1. Ensure that all of the information is correct in the Master DMAS Information spreadsheet.
  https://docs.google.com/spreadsheets/d/1lyvAeoUTji-FGH_Fz-hGWQOnEWJb2EMhWgc7LKz2ix0/edit

  *Check both the collection sheet for the collection where the new model will be added and the models sheet, where the publication information will be.*

2. Log into your account on DMAS, creating one if necessary.
  http://dmas.berkeley.edu/

  *Any model you create will be associated with your account, and will initially only be viewable by that account.*

3. Create an API key and record it.
  http://dmas.berkeley.edu/api/initialize

  *Your API key will be required for most DMAS operations outside of the website, and uniquely identifies you as the user.*

4. Run the commands above to install `rdmas`.

## Adding a model

Now that you have everything set up to add models, the following walks you though adding one.  We will assume that you are sharing your estimate with the GCP community.

1. Identify the "Unique ID" on the Master DMAS Information spreadsheet for the estimate you will be adding, or add a new one.  Switch to the "Models" sheet to find and add unique IDs.
  https://docs.google.com/spreadsheets/d/1lyvAeoUTji-FGH_Fz-hGWQOnEWJb2EMhWgc7LKz2ix0/edit

  *This spreadsheet has all of the meta-information for the estimate, like publication and units.  If you don't have a specific item you want to add, choose any Unique ID.*

1. Run your regression.  If you don't already have a regression that you want to upload, try one of the tutorials below.

3. After you have run your regression, execute the following command:
   ```dmas.put.model([LM or FELM Model], [Your API Key], [The GCP Spreadsheet Key])```

  *This will call DMAS with all of the information in your regression, displaying both the URL used and the result, which will be a DMAS ID for your regression.*

  *Note: If the model includes fixed effects or other dummy variables, the upload time can be greatly improved by adding an optional "coefficient count" argument to the `dmas.put.model` command, specifying that only that many coefficients should be uploaded to DMAS.*

4. Record the hexidecimal value it returns, as you will need this in step 6.  If you are sharing this with the GCP community, fill in the DMAS ID returned by dmas.put.model into the master spreadsheet.
  https://docs.google.com/spreadsheets/d/1lyvAeoUTji-FGH_Fz-hGWQOnEWJb2EMhWgc7LKz2ix0/edit

  *Once you have put in the DMAS ID for a given model, subsequent calls to dmas.put.model will replace the information in this object.  You may see the error “server refused to send file”, which just means that the ID returned is the same.*

5. Check to see that your result has shown up in your accounts list of estimates, at
  http://dmas.berkeley.edu/model/list_estimates

  *Estimates are subtly different from models, so you will only see your R estimates here.*

6. Execute one of the four "model extraction" commands, defined below.

  *This will actually create the model in DMAS.  You could extract multiple models from a single R regression.*

7. Use the link returned by the command to make sure that the model came through as expected.

## Model Extraction Commands and Tutorials

### Single Variable Models: `dmas.extract.single`

A single variable model describes a coefficient through its probability distribution (a Gaussian at the estimated value, with the standard error as its standard deviation).

**Syntax:**
```dmas.extract.single([Your API Key], [Coefficient Name], [GCP Spreadsheet Key], <DMAS Estimate ID>)```

If you do not specify the last argument (the ID), the most recent result from `dmas.put.model` will be used.

**Example:**
```
mod <- lm(Sepal.Length ~ Petal.Length + Species, data=iris)

dmas.put.model(mod, "4sW2Txtsn8o3bkwY", "James-RTest")
dmas.extract.single("4sW2Txtsn8o3bkwY", "Petal.Length", "James-RTest")
```

### Polynomial estimates: `dmas.extract.polynomial`

Polynomial estimates have some collection of coefficients for an N-order polynomial.

**Syntax:**
```dmas.extract.polynomial([Your API Key], [Vector of Coefficients], [Lower Bound], [Upper Bound], [GCP Spreadsheet ID], <DMAS Estimate ID>)

If you do not specify the last argument (the ID), the most recent result from `dmas.put.model` will be used.

**Example:**
```
width <- iris$Sepal.Width
width2 <- width^2
width3 <- width^3
mod <- lm(Sepal.Length ~ width + width2 + width3, data=iris)

dmas.put.model(mod, "4sW2Txtsn8o3bkwY", "James-RTest")
dmas.extract.polynomial("4sW2Txtsn8o3bkwY", c("(Intercept)", "width", "width2", "width3"), 1, 5, "James-RTest")
```

### Binned Variable Models: `dmas.extract.binned`

A binned variable model describes a non-linear response, using data that falls into specific independent variable bins.

**Syntax:**
```dmas.extract.binned([Your API Key], [Vector of End Points], [Vector of Coefficients], [GCP Spreadsheet Key], <DMAS Estimate ID>)```

Use the coefficient name `drop` for the bin that is dropped.

If you do not specify the last argument (the ID), the most recent result from `dmas.put.model` will be used.

```
mod <- lm(Sepal.Length ~ Petal.Length + Species, data=iris)

dmas.put.model(mod, "4sW2Txtsn8o3bkwY", "James-RTest")
dmas.extract.binned("4sW2Txtsn8o3bkwY", c(0, 1, 2, 3), c("Speciesversicolor", "drop", "Speciesvirginica"), "James-RTest")
```