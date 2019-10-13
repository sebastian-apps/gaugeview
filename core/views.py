from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.http import JsonResponse
from django.http import HttpResponse
import json
import csv
from django.utils.encoding import smart_str

import gauge_monitor



def gaugeview(request):
    """ Create the template for GaugeView and initialize with arbitrary values. """
    context = gauge_monitor.default_values()
    return render(request, 'core/gaugeview.html', context)



def read_gauge(request):
    """ Process gauge image """

    try:
        if request.method == 'POST':
            image_string = request.POST.get('image_string') # from webcam
            comp_ratio = float(request.POST.get('comp_ratio'))
            radius = int(request.POST.get('radius'))
            sensitivity = float(request.POST.get('sensitivity'))
            r_factor = float(request.POST.get('r_factor'))
            sm_r_factor = float(request.POST.get('sm_r_factor'))
            pxls_detected_min = int(request.POST.get('pxls_detected_min'))
            r_sq_min = float(request.POST.get('r_sq_min'))
            residual_cutoff = float(request.POST.get('residual_cutoff'))
            ref_angle = float(request.POST.get('ref_angle'))
            calib = float(request.POST.get('calib'))


            return JsonResponse(gauge_monitor.read( image_string, comp_ratio, radius,
                                                    sensitivity, r_factor, sm_r_factor,
                                                    pxls_detected_min, r_sq_min,
                                                    residual_cutoff, ref_angle, calib))

    except Exception as e:
        print(str(e))

    return HttpResponse(status=400)



def gauge_export(request):
    """ Export recorded data to CSV. """

    datapoints = json.loads(request.POST['json'])

    if request.method == 'POST':

        # response content type
        response = HttpResponse(content_type='text/csv')
        #decide the file name
        response['Content-Disposition'] = 'attachment; filename="GaugeView-Output.csv"'
        writer = csv.writer(response, csv.excel)
        response.write(u'\ufeff'.encode('utf8'))

        #write the headers
        writer.writerow([
        	smart_str("Time (s)"),
        	smart_str("Pressure (psig)"),
        ])
        for datapoint in datapoints:
            writer.writerow([
            	smart_str(datapoint["x"]),
            	smart_str(datapoint["y"]),
            ])
        return response
    else:
        return HttpResponse("Export Failed")
