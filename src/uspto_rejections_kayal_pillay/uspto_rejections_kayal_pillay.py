import requests
import pandas as pd
import re
import numpy as np
import json
from json import dumps, loads
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
import plotly.express as px

def all_patents(number_rows = 100000):
    """
    Returns Pandas DataFrame containing all patent information in API, including details such as rejection reason for each patent by default. User can request lower number of rows.
    
    Parameters
    ----------
    number_rows: int
        Integer input; total number of rows in API in 100,000, though user can request for lower number.
    
    Returns
    -------
    Pandas DataFrame
        The default output is a dataframe containing all patent information in API, including details such as rejection reason for each patent. User can request a lower number of rows.

    Examples
    --------
    >>> import uspto_rejections_kayal_pillay
    >>> all_patents()
    >>> all_patents(50)
    
    """
    assert isinstance(number_rows, int), "Enter number of rows as integer. Maximum is 100,000."

    #obtaining data from API
    url = "https://developer.uspto.gov/ds-api/oa_rejections/v2/records"
    criteria = 'criteria=*%3A*&start=0&rows=100001'
    headers = {'Content-Type': 'application/x-www-form-urlencoded','Accept': 'application/json'}
    x = requests.post(url, data=criteria, headers=headers, verify=False) 
    
    assert x.status_code == 200, "Request is unsuccessful. Check input." #200 is sucessful, 404 in invalid

    #conversion of data in pandas dataframe
    data = x.json()
    patents_df = pd.DataFrame(data["response"]["docs"])
    
    print(f"Status Code: {x.status_code}. Request successfully executed.")
    return patents_df

def year_seperator(number_rows = 100000):
    """
    Returns cleaned dataframe to be used in further analysis after splitting submission date (ddmmyyy + timezone) into a separate clean year column for data analysis.
    
    Parameters
    ----------
    number_rows: int
        Integer input; total number of rows in API in 100,000, though user can request for lower number.
    
    Returns
    -------
    Pandas Dataframe
        The output is a dataframe filtered by the input year. 

    Examples
    --------
    >>> year_seperator()
    
    """
    assert isinstance(number_rows, int), "Enter rows as integer."
    
    #splitting submissionDate columnn into new year column, for filtering based on year
    df = all_patents()
    df["submissiondateclean"]= df["submissionDate"].apply(lambda x : x[:10])
    df['submissiondateclean']=df['submissiondateclean'].apply(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d").year)

    return df

def patent_reject(patent_application_number):
    """
    Returns dataframe showing all rejection details of that particular patent, including submission date and rejection reason, which is useful as in the API, some patent application numbers have numerous entries. Dataframe comes with clean submission year column.
    
    Parameters 
    ----------  
    patent_application_number: str
        String input of numbers; this is the patent application number of the patent one wants information on.
        
    Returns
    -------
    Pandas Dataframe
        The output is a dataframe containing all information on that particular rejected patent compiled into a single dataframe, with clean submission year column.

    Examples
    --------
    >>> patent_reject('14983812')
    
    """
    assert isinstance(patent_application_number, str), "Enter patent application number as a string."
    patent_df = year_seperator()
    single_patent = patent_df[patent_df["patentApplicationNumber"] == f"{patent_application_number}"]
        
    return single_patent

def rejection_filter(reject_reason):
    """
    Returns Pandas DataFrame containing all patent information for those patents rejected for reason in filter, with clean submission year column.
    
    Parameters
    ----------
    reject_reason: str
        String input of alphabets and numbers; this is the rejection reason user wishes to filter API on.
    
    Returns
    -------
    Pandas DataFrame
        The output is a dataframe containing all patent information in API on patents rejected for the reason chosen, with clean submission year column.

    Examples
    --------
    >>> rejection_filter('headerMissing')
    >>> rejection_filter('formParagraphMissing')
    
    """
    assert isinstance(reject_reason, str), "Enter rejection reason as string"

    #ensuring that inputs are acceptable and providing user with information on what the possible inputs are if they are incorrect
    possible_rejection_reasons = {
                                "headerMissing",
                                "formParagraphMissing",
                                "rejectFormMissmatch",
                                "closingMissing",
                                "hasRej101",
                                "hasRejDP",
                                "hasRej102",
                                "hasRej103",
                                "hasRej112",
                                "hasObjection",
                                "cite102GT1",
                                "cite103GT3",
                                "cite103EQ1",
                                "cite103Max"
                                 }
                                 
    assert reject_reason in possible_rejection_reasons, f"Check input on reason for rejection. Only the following rejection reasons are permitted: {possible_rejection_reasons}"
    
    df = year_seperator()
    patent_df = df.replace({1.0 : '1', 0.0 : '0', True: '1', False : '0'}) #API inputs ranged from floats to bool. Standardised. Use of for loop possible, but more computationally heavy.
    filtered_df = patent_df[patent_df[f"{reject_reason}"] == "1"]

    return filtered_df

def rejection_graph(reject_reason):
    """
    Returns line graph showing number of patents rejected for a particular reason over the years. 
    
    Parameters
    ----------
    reject_reason: str
        String input of alphabets and numbers; this is the rejection reason user wishes to filter API on.
    
    Returns
    -------
    Plotly Express graph
        The output is a line graph visualising number of patents rejected for the chosen reason over the years.

    Examples
    --------
    >>> rejection_graph('headerMissing')
    
    """
    assert isinstance(reject_reason, str), "Enter rejection reason as string" #as this function passes through rejection_filter, the other assertions are not repeated.

    df = rejection_filter(reject_reason)

    a = df[[f'{reject_reason}', 'submissiondateclean']].groupby('submissiondateclean').count()
    b = a.reset_index()
    fig = px.line(
      data_frame = b,
      x="submissiondateclean",
      y= f'{reject_reason}',
      title = f'Number of rejections for {reject_reason} by year')

    return fig

def type_rejections_crosstab(submission_year, normalise = False):
    """
    Returns Pandas DataFrame containing crosstab of the proportion of final rejections ("CTFR") and non-final rejections ("CTNF") in a given year. Allows user to customise whether they want crosstab normalised (in proportions) or in raw numbers.

    Parameters
    ----------
    submission_year: int
        Integer input; this is the year user wishes to filter API on.
    
    normalise: bool
        Boolean input; choice of whether to normalise the crosstab data or not (default).
    
    Returns
    -------
    Pandas Crosstab
        The output is a crosstab containing proportion of type of rejections in the filtered year. If not normalised, crosstab contains raw numbers of applications.

    Examples
    --------
    >>> type_rejections_crosstab(2020)
    >>> type_rejections_crosstab(2020, normalise = True)
    
    """
    assert isinstance(submission_year, int), "Enter year as integer."
    assert isinstance(normalise, bool), "Enter either True or False (boolean input)."

    #assertions to deal with scope of API -- from 2018 till 3 months from current date
    assert submission_year >= 2018, "API only collates records from 2018." #lower bound

    currentTimeDate = datetime.datetime.now() - relativedelta(months=3) #using datetime function in datetime module minus 3 months
    current_year = currentTimeDate.strftime("%Y") #datetime object extraction of year
    current_year_int = int(current_year) #conversion to integer for assertion purposes
    assert submission_year <= current_year_int, "API only collates records till 3 months from current date."

    df = year_seperator(submission_year)
    by_year = df[df["submissiondateclean"] == submission_year] #filter by year
    crosstab_normalise = pd.crosstab(by_year.submissiondateclean, [by_year.legacyDocumentCodeIdentifier], normalize='all') #only unique values are CTNF and CTFR - no NaN.
    crosstab_notnorm = pd.crosstab(by_year.submissiondateclean, [by_year.legacyDocumentCodeIdentifier])

    if normalise == True:
      return crosstab_normalise
    else: 
      return crosstab_notnorm

def type_rejections_overall(number_rows = 100000, normalise = False):
    """
    Returns Pandas DataFrame containing crosstab of the proportion of final rejections ("CTFR") and non-final rejections ("CTNF") for all years in API, with breakdown of proportion per year. Allows user to customise whether they want crosstab normalised (in proportions) or in raw numbers.

    Parameters
    ----------
    number_rows: int
        Integer input; total number of rows in API in 100,000, though user can request for lower number.
    
    normalise: bool
        Boolean input; choice of whether to normalise the crosstab data or not (default).
     
    Returns
    -------
    Pandas Crosstab
        The output is a crosstab containing proportion of type of rejections. If not normalised, crosstab contains raw numbers of applications.

    Examples
    --------
    >>> type_rejections_overall()
    >>> type_rejections_overall(50, True)
    
    """
    assert isinstance(number_rows, int), "Enter rows as integer."
    assert isinstance(normalise, bool), "Enter either True or False (boolean input)."

    df = year_seperator()
    crosstab = pd.crosstab(df.submissiondateclean, [df.legacyDocumentCodeIdentifier], normalize='all') #only unique values are CTNF and CTFR - no NaN.
    crosstab_notnorm = pd.crosstab(df.submissiondateclean, [df.legacyDocumentCodeIdentifier])
        
    if normalise == True:
      return crosstab
    else: 
      return crosstab_notnorm

def actiontype_bycategory(category):
    """
    Returns Pandas DataFrame compiling all the entries for the requested action type category, as presently the API data has several variations in spelling for same category. This also has a clean year column based on submission date.

    Parameters
    ----------
    category: str
        String input; pre-set list of categories to capture the various spellings of the actiontypecategory column in API. Categories are "reject", "withdraw", "cancel", "object", "allowed", "allowable", "interpret".
    
    Returns
    -------
    Pandas Dataframe
        The output is a dataframe already filtered by the action type category, with clean submission year column. 

    Examples
    --------
    >>> actiontype_bycategory("reject")
    
    """
    assert isinstance(category, str), "Enter category as string."
    assert category in ["reject", "withdraw", "cancel", "object", "allowed", "allowable", "interpret"], "Only categories accepted are reject, withdraw, cancel, object, allowed, allowable, interpret."
   
    df = year_seperator()
    reject_df = df[(df['actionTypeCategory'].str.contains("reject"))]
    withdraw_df = df[(df['actionTypeCategory'].str.contains("with"))]
    cancel_df = df[(df['actionTypeCategory'].str.contains("canc"))]
    object_df = df[(df['actionTypeCategory'].str.contains("obj"))]
    interpret_df = df[(df['actionTypeCategory'].str.contains("interpret"))]
    allowed_df = df[(df['actionTypeCategory'].str.contains("allowe")) | (df['actionTypeCategory'].str.contains("allow\s"))]
    allowable_df = df[(df['actionTypeCategory'].str.contains("allowa"))] #allowable category refers to case when patents claims would be allowable if filer manages to overcome certain objections. This differs from allowed claims.

    if category == "reject":
        return reject_df
    if category == "withdraw":
        return withdraw_df
    if category == "cancel":
        return cancel_df
    if category == "object":
        return object_df
    if category == "interpret":
        return interpret_df
    if category == "allowed":
        return allowed_df
    if category == "allowable":
        return allowable_df

def actiontype_clean(number_rows = 100000):
    """
    Returns clean Pandas DataFrame changing all the entries for the action type to standardise forms, as presently the API data has several variations in spelling for same category. This also has a clean year column based on submission date.

    Parameters
    ----------
    number_rows: int
        Integer input; total number of rows in API in 100,000, though user can request for lower number.
    
    Returns
    -------
    Pandas Dataframe
        The output is a dataframe with standardised entries under action type, with clean submission year column. 

    Examples
    --------
    >>> actiontype_clean()
    >>> actiontype_clean(100)
    
    """
    assert isinstance(number_rows, int), "Enter number of rows as integer."
   
    df = year_seperator()

    #set of compiled regular expressions for various unique action types in raw API data, for current unique types (i.e., misspellings)
    rejected = re.compile(r'\breject\S*') #reject matches start of a word (not the entire string), to account for potentially having two different labels in one entry
    objection = re.compile(r'\bobject\S*') #same as above, re object
    withdrawn = re.compile(r'withdr(a|e)\S*') 
    cancelled = re.compile(r'\bcancel(\s|\S*)')
    interpretation = re.compile(r'\binterpr\S*')
    allowed = re.compile(r'\ballow(ed\s|ed\S*|\s)')
    allowable = re.compile(r'\ballowa\S*') #allowable category refers to case when patents claims would be allowable if filer manages to overcome certain objections. This differs from allowed claims.

    #creating dictionary for replacement
    dict = {rejected : 'Rejected', objection : 'Objection', withdrawn: 'Withdrawn', cancelled : 'Cancelled', interpretation : 'Interpretation Issue', allowed : 'Allowed', allowable : 'Allowable if objection resolved'}

    df_updated = df.replace({"actionTypeCategory": dict}, regex = True)
    return df_updated