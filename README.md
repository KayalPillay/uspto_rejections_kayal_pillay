# uspto_rejections_kayal_pillay

Package to interact with the USPTO Rejections API (https://developer.uspto.gov/api-catalog/uspto-office-action-rejection-api)

## Installation

```bash
$ pip install uspto_rejections_kayal_pillay
```

## Usage

Presently existing packages for the US Patents and Trademarks Office (USPTO) deal with data involving accepted patents - e.g., https://pypi.org/project/pypatent/. This package specifically deals with patents that were rejected so that those intending to file future patents are well-informed. 

The following functions can be found within this package:

a) all_patents: Returns Pandas DataFrame containing all patent information in API, including details such as rejection reason for each patent by default. User can request lower number of rows.

b) year_seperator: Returns cleaned dataframe to be used in further analysis after splitting submission date (ddmmyyy + timezone) into a separate clean year column for data analysis.

c) patent_reject: Returns dataframe showing all rejection details of that particular patent, including submission date and rejection reason, which is useful as in the API, some patent application numbers have numerous entries. Dataframe comes with clean submission year column.

d) rejection_filter: Returns Pandas DataFrame containing all patent information for those patents rejected for reason in filter, with clean submission year column.

e) rejection_graph: Returns line graph showing number of patents rejected for a particular reason over the years. 

f) type_rejections_crosstab: Returns Pandas DataFrame containing crosstab of the proportion of final rejections ("CTFR") and non-final rejections ("CTNF") in a given year. Allows user to customise whether they want crosstab normalised (in proportions) or in raw numbers.

g) type_rejections_overall: Returns Pandas DataFrame containing crosstab of the proportion of final rejections ("CTFR") and non-final rejections ("CTNF") for all years in API, with breakdown of proportion per year. Allows user to customise whether they want crosstab normalised (in proportions) or in raw numbers.

h) actiontype_bycategory: Returns Pandas DataFrame compiling all the entries for the requested action type category, as presently the API data has several variations in spelling for same category. This also has a clean year column based on submission date.

i) actiontype_clean: Returns clean Pandas DataFrame changing all the entries for the action type to standardise forms, as presently the API data has several variations in spelling for same category. This also has a clean year column based on submission date.

Below is a 1:1 mapping of the various rejection terms used in the rejection reasons in the API, and their meaning:

                    "headerMissing",                   :    does not include standard headings or contains no headings
                    
                    "formParagraphMissing",            :    does not contain the form paragraph(s) for the rejection(s) raised
                    
                    "rejectFormMissmatch",             :    form paragraph(s) do not match the rejection(s) raised in  action sentence(s)
                    
                    "closingMissing",                  :    examiner is to provide specific contact information at end - missing here
                    
                    "hasRej101",                       :    Title 35 of the United States Code, section 101 (35 U.S.C. §101) rejection 
                    
                    "hasRejDP",                        :    non-statutory double patenting rejection
                    
                    "hasRej102",                       :    35 U.S.C. §102 rejection
                    
                    "hasRej103",                       :    35 U.S.C. §103 rejection
                    
                    "hasRej112",                       :    35 U.S.C. §112 rejection
                    
                    "hasObjection",                    :    whether an objection is raised
                    
                    "cite102GT1",                      :    Greater than One Citation in 102 Rejection
                    
                    "cite103GT3",                      :    Greater than Three Citations in 103 Rejection
                    
                    "cite103EQ1",                      :    One Citation in 103 Rejection
                    
                    "cite103Max"                       :    Maximum Citations in 103 Rejection

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`uspto_rejections_kayal_pillay` was created by Kayal Pillay (mmp2227). It is licensed under the terms of the MIT license.

## Credits

`uspto_rejections_kayal_pillay` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
