#' Extracting a single coefficient model
#'
#' Identify a model for use in DMAS after uploading it with dmas.put.model.
#' @param apikey API Key provided by DMAS
#' @param coeffs A coefficient name
#' @param infoid An InfoID (gcp or from the DMAS spreadsheet)
#' @param id ID returned by dmas.put.model (or NA for last)
#' @export
dmas.extract.single <- function(apikey, coeff, infoid, id=NA) {
    if (is.na(id)) {
        print("id not provided; using last result")
        id <- DMAS_LAST_RESULT
    }

    dmas.urlstr <- sprintf("extract_estimate_single?apikey=%s&coeff=%s&infoid=%s&id=%s", apikey, coeff, infoid, id)

    dmas.get.api(dmas.urlstr, as.model=T)
}

