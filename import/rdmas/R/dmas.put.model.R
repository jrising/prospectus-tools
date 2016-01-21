#' Sending a model to the DMAS server
#'
#' Send all model data to DMAS
#' @param model And LM or FELM model
#' @param apikey API Key provided by DMAS
#' @param infoid An InfoID (gcp or from the DMAS spreadsheet)
#' @param varnum An optional number of coefficients to upload
#' @export

dmas.put.model <- function(model, apikey, infoid, varnum=NA) {
    require(gtools)

    print("Uploading to DMAS...")

    B <- model$coeff
    if (is.na(varnum) || varnum > length(B))
        varnum <- length(B)

    dmas.get.api("make_queue", F, quietly=T)
    progressV <- 100 * 4/7
    progressB <- 100 * 1/7
    progressNames <- 100 * 1/7
    progressOther <- 100 * 1/7

    cmdline2 <- substr(gsub("#", "%23", capture.output(model$call)), 1, 100)

    summy <- summary(model)

    Xstr <- sprintf("apikey=%s&infoid=%s&df=%d&sigma=%f&r2=%f&r2_adj=%f", apikey, infoid, model$df.residual, summy$sigma, summy$r.squared, summy$adj.r.squared)
    if (class(model) == "lm") {
        Xstr <- paste0(Xstr, sprintf("&N=%d&fstat_value=%f&fstat_numdf=%f&fstat_dendf=%f", length(model$residuals), summy$fstatistic[1], summy$fstatistic[2], summy$fstatistic[3]))
    } else if (class(model) == "felm") {
        Xstr <- paste0(Xstr, sprintf("&N=%d&TSS=%f&P_TSS=%f&fstat_value=%f&fstat_numdf=%f&fstat_dendf=%f&pval=%f&P_r2=%f&P_r2_adj=%f&rse=%f&rdf=%d", model$N, model$TSS, model$P.TSS, summy$F.fstat[1], summy$F.fstat[2], summy$F.fstat[3], summy$pval, summy$P.r.squared, summy$P.adj.r.squared, summy$rse, summy$rdf))
    }
    Xstr <- gsub(" ", "+", Xstr)

    print("Constructing V matrices...")

    Vstr <- ""
    if (class(model) == "felm")
        V <- model$robustvcv
    else
        V <- vcov(model)
    totalV <- varnum * varnum
    for (ii in 1:varnum) {
        for (jj in 1:varnum) {
            if (nchar(Vstr) > 800) { # send to server if too much
                dmas.get.api(paste0("queue_arguments?V=", Vstr), F, quietly=T)
                Vstr <- ""

                print(paste("Progress:", progressV * (ii * varnum + jj) / totalV, "%"))
            }

            Vstr <- paste0(Vstr, ",", V[ii, jj])
        }
    }

    print("Constructing beta vector...")

    Bstr <- ""
    for (ii in 1:varnum) {
        if (nchar(Bstr) > 800) { # send to server if too much
            dmas.get.api(paste0("queue_arguments?b=", Bstr), F, quietly=T)
            Bstr <- ""
            print(paste("Progress:", progressV + progressB * ii / varnum, "%"))
        }

        Bstr <- paste0(Bstr, ",", B[ii])
    }

    print("Constructing coefficient names...")

    if (class(model) == "felm")
        conames <- paste(rownames(B)[1:varnum], collapse=",")
    else
        conames <- paste(names(B)[1:varnum], collapse=",")
    conames <- gsub("#", "%23", conames)

    while (nchar(conames) > 800) {
        sendconames <- substr(conames, 1, 800)
        dmas.get.api(paste0("queue_arguments?names=", sendconames), F, quietly=T)
        conames <- substr(conames, 801, nchar(conames))
        print(paste("Progress:", progressV + progressB + progressNames * 800 / max(800, nchar(conames))))
    }

    if (nchar(Xstr) + nchar(Vstr) + nchar(Bstr) + nchar(conames) > 800) {
        if (nchar(Xstr) > 250) {
            dmas.get.api(paste0("queue_arguments?", Xstr), F, quietly=T)
            Xstr <- ""
        }
        if (nchar(Vstr) > 250) {
            dmas.get.api(paste0("queue_arguments?V=", Vstr), F, quietly=T)
            Vstr <- ""
        }
        if (nchar(Bstr) > 250) {
            dmas.get.api(paste0("queue_arguments?b=", Bstr), F, quietly=T)
            Bstr <- ""
        }
        if (nchar(conames) > 250) {
            dmas.get.api(paste0(paste0("queue_arguments?names=", names)), F, quietly=T)
            conames <- ""
        }
    }

    print("Completing model...")

    dmas.get.api(paste0("call_with_queue?method=put_r_estimate&", Xstr, "&V=", Vstr, "&b=", Bstr, "&names=", conames), F, quietly=T)
}
