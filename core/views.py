from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404, JsonResponse, HttpResponse
from django.urls import reverse
from .models import Datasets
from .forms import DatasetsForm
import scipy.stats as st
import json
import numpy as np
import math
import statistics
from statsmodels.stats.power import  tt_ind_solve_power


DEC = 4  # Round values to a constant number of decimal places.




class Data:
    """
    An instance represents one dataset. Each instance calculates its own descriptive statistics.
    Data instances can be compared to calculate inferential statistics.
    """
    def __init__(self, dataset):
        self.dataset = dataset
        self.calc_descriptive_stats()


    def calc_descriptive_stats(self):
        self.mean = statistics.mean(self.dataset)
        self.sd = statistics.stdev(self.dataset)
        self.n = len(self.dataset)
        self.df = self.n - 1  # degrees of freedom
        self.dist = [] # distribution
        self.step_size = 0;


    def create_t_dist(self, min, max, ncp):
        """ Create x,y coordinates of t distribution for a given range. """
        self.step_size = (max - min) / 200   # 200 is an arbitrary number
        t_list = [round(min + self.step_size*i, 6) for i in range(0, 200)]

        try:
            coords = []
            for t in t_list:
                y = round((math.gamma((self.df+1)/2)/(math.sqrt(self.df*math.pi)*math.gamma(self.df/2))) * (1+((t**2)/self.df))**(-(self.df+1)/2),DEC)
                coords.append({'x': t + ncp, 'y': y})
            self.dist = coords

        except Exception as e:
            print(str(e))
            self.dist = []



    def __str__(self):
        return str(self.clean())

    def clean(self):
        return {
            "dataset": self.dataset,
            "dist": self.dist,
            "step_size": self.step_size,
            "mean": round(self.mean, DEC),
            "sd": round(self.sd, DEC),
            "n": self.n,
            "df": self.df,
        }






def ttest(request):

    model_instance = None
    test_results = {}
    axes = {}

    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = DatasetsForm()
        # Default datasets
        dataset1 = [87, 101, 64, 86, 87, 82, 70]
        dataset2 = [100, 124, 93, 114, 123, 130, 136]
        form.fields['dataset1'].initial = prep_for_form(dataset1)
        form.fields['dataset2'].initial = prep_for_form(dataset2)

    else:
        # POST data submitted; process data.
        request.POST._mutable = True
        print(request.POST)
        form = DatasetsForm(data=request.POST)
        if form.is_valid():
            model_instance = form.save(commit=False)
            dataset1 = clean_dataset(model_instance.dataset1)
            dataset2 = clean_dataset(model_instance.dataset2)
            # Add here any changes before saving to database
            model_instance.save()

        else: # form not valid
            context = {'form': form }
            return render(request, 'core/ttest.html', context)

    try:

        data1 = Data(dataset1)
        data2 = Data(dataset2)

        # data1.mean = 5
        # data1.sd = 15
        # data1.n = 42
        # data1.df = data1.n - 1
        # data2.mean = 15
        # data2.sd = 17
        # data2.n = 42
        # data2.df = data2.n - 1

        # Sample with largest mean will be group 2
        if data1.mean > data2.mean:
            data1, data2 = data2, data1
            form.data['dataset1'] = prep_for_form(data1.dataset)
            form.data['dataset2'] = prep_for_form(data2.dataset)

        # Get inferential statistics
        df = get_pooled_df(data1, data2) # degrees of freedom

        t_value, p_value = get_t_and_p_value(data1, data2, df)
        effect_size, ncp = get_effect_size_ncp(data1, data2)

        # Define chart's x-axis range.
        x_min, x_max = get_x_axis_min_max(data1, data2)
        # Get distribution x,y values for plotting.
        data1.create_t_dist(x_min, x_max, 0)
        data2.create_t_dist(x_min, x_max, ncp)


        # Configure the x-axis step size for a more visually appealing chart.
        if data1.step_size > data2.step_size:
            step_size = data1.step_size
        else:
            step_size = data2.step_size

        if step_size >= 1:  # If step_size > 1, eliminate decimal places.
            step_size = int(step_size)
            x_min = int(x_min)
            x_max = int(x_max)

        # Define chart's y-axis range: 0 to y_max. Multiply by arbitrary value to provide headspace.
        y_max = 1.2 * get_y_axis_max(data1.dist, data2.dist)

        test_results.update({"df" : df, "p_value" : p_value, "t_value" : t_value,
                             "effect_size": effect_size, "ncp" : ncp
                             })

        test_results.update({"crit_t_init": st.norm.ppf(.95)})  # Arbitrary starting point (alpha=0.05), opposite is st.norm.cdf(1.64)
        axes.update({"x_min": x_min, "x_max": x_max, "y_max": y_max, "step_size": step_size})


    except Exception as e:
        print(str(e))



    context = { 'form': form, 'data1': data1.clean(), 'data2': data2.clean(),
                'test_results': test_results, 'axes': json.dumps(axes),
              }
    return render(request, 'core/ttest.html', context)







def get_pooled_df(data1, data2):
    # Get pooled degrees of freedom
    v1 = data1.df
    v2 = data2.df
    df = (((data1.sd**(2)/data1.sd)+(data2.sd**(2)/data2.sd))**(2))/(((data1.sd**(4)/(v1*data1.sd**(2))))+((data2.sd**(4)/(v2*data2.sd**(2)))))
    return math.trunc(round(df,0))


def get_t_and_p_value(data1, data2, df):
    t = (data1.mean - data2.mean)/math.sqrt((data1.sd**(2)/data1.n)+(data2.sd**(2)/data2.n))
    p_value = st.t.sf(np.abs(t), df)   # two-sided p_value = st.t.sf(np.abs(t), df) * 2
    return round(t,DEC), round(p_value,DEC)


def get_effect_size_ncp(data1, data2):
    mean_difference = data1.mean - data2.mean
    num = ((data1.n - 1)*(data1.sd**(2))) + ((data2.n - 1)*(data2.sd**(2)))
    den = data1.n + data2.n - 2
    sd = math.sqrt(num/den)  # pooled sd
    es = abs(mean_difference / sd)
    nobs_ratio = data1.n / data2.n

    # error check front-side power calculation with backend power calculation
    power = tt_ind_solve_power(effect_size=es, nobs1=data1.n, alpha=0.05, ratio=nobs_ratio, alternative='larger')
    print("POWER ",power)

    p = 1./ (1./data1.n  + 1./data2.n)  # from statsmodels library code
    ncp = es*math.sqrt(p)
    return round(es, DEC), ncp




def get_x_axis_min_max(data1, data2):
    # Each tail of each distribution will have at least 2 * sd/sqrt(n) represented visually.
    vals = []
    vals.append(round(0 - (2 * data1.sd/(math.sqrt(data1.n))), 6))
    vals.append(round(0 + (2 * data1.sd/(math.sqrt(data1.n))), 6))
    vals.append(round(0 - (2 * data2.sd/(math.sqrt(data2.n))), 6))
    vals.append(round(0 + (2 * data2.sd/(math.sqrt(data2.n))), 6))
    return min(vals), max(vals)


def get_y_axis_max(dist_dist1, dist_dist2):
    l1 = [coord.get('y') for coord in dist_dist1]
    l2 = [coord.get('y') for coord in dist_dist2]
    return max(l1 + l2)



def prep_for_form(num_list):
    # Prep list for output in dataset form field
    return str(num_list).replace(", ","\n").replace("[","").replace("]","")


def clean_dataset(dataset):
    # Some cleaning done at the model level. Additional cleaning
    # may be performed here.
    dataset = dataset.splitlines()
    try:
        dataset = [float(data) for data in dataset]
    except ValueError:
        return []
    return dataset




# Functions below are not currently used.
#
# def get_normal_dist(data, min, max):
#     """ Return x,y coordinates of normal distribution. Useful for z-tests. """
#     print(data)
#     try:
#         coords = []
#         for x in range(min, max + 1):
#             y = round((1/(data.sd*math.sqrt(2*math.pi)))*math.exp((-((x-data.mean) ** 2))/(2*data.sd ** 2)),DEC)
#             coords.append({'x': x, 'y': y})
#         return coords
#     except Exception as e:
#         print(str(e))
#         return []
#
#
# def get_effect_size(data1, data2):
#     mean_difference = data1.mean - data2.mean
#     num = ((data1.n - 1)*(data1.sd**(2))) + ((data2.n - 1)*(data2.sd**(2)))
#     den = data1.n + data2.n - 2
#     pooled_sd = math.sqrt(num/den)  # pooled sd
#     return round(abs(mean_difference / pooled_sd),DEC)
