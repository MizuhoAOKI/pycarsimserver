# Simple visualizer of vehicle trajectory in svg format.
import numpy as np

# set svg template path
SVG_TEMPLATE_PATH = './template/svg_template.svg'

def svg_visualizer(timestamp, car_x_ary, car_y_ary, outputpath, svgtemplate=SVG_TEMPLATE_PATH):

    # Set parameters
    MARGIN_RATE = 10 # % of maximum width/height
    MIN_MARGIN_X = 100 # px
    MIN_MARGIN_Y = 100 # px
    DATA_SCALE = 10 # rate of magnification compared to the car
    FF_SCALE = 1.0 # default: 1 means normal(1x) speed.
    SIM_TIME = timestamp[-1]

    # Load svg template
    svg_template = open(SVG_TEMPLATE_PATH)
    output =  svg_template.read()
    svg_template.close()

    # Turn the y-axis upside down
    maximum_y = max(car_y_ary)
    car_y_ary = maximum_y - car_y_ary

    # Scale data
    car_x_ary *= DATA_SCALE
    car_y_ary *= DATA_SCALE

    # Get several info from trajectory log
    min_x, max_x = min(car_x_ary), max(car_x_ary)
    min_y, max_y = min(car_y_ary), max(car_y_ary)
    path_length = np.cumsum([np.hypot(dx, dy) for dx, dy in zip(np.diff(car_x_ary), np.diff(car_y_ary))]).tolist()
    path_length.insert(0, 0.0)

    # Set margin and viewbox size
    margin_x = max( (max_x - min_x) * MARGIN_RATE / 100.0, MIN_MARGIN_X)
    margin_y = max( (max_y - min_y) * MARGIN_RATE / 100.0, MIN_MARGIN_Y)
    viewbox_width  = ((max_x + margin_x) - (min_x - margin_x))
    viewbox_height = ((max_y + margin_y) - (min_y - margin_y))

    # Set start point of the path.
    svg_path_code = "M " + str(car_x_ary[0]+margin_x) + "," + str(car_y_ary[0]+margin_y) + ", L"

    # Set viewbox 
    viewbox_code = str(min_x) + "," + str(min_y) + "," + str(viewbox_width) + "," + str(viewbox_height)

    # Set vehicle trajectory
    for i in range(len(timestamp)):
        svg_path_code += " " + str(car_x_ary[i] + margin_x) + "," + str(car_y_ary[i] + margin_y) + " "

    # Set keytimes and keypoints to express velocity variation. 
    keytimes_code  = ""
    keypoints_code = ""
    for i in range(len(timestamp)):
        keytimes_code  += str(timestamp[i] / SIM_TIME)
        keypoints_code += str(path_length[i] / path_length[-1]) # Don't be over 1.0
        if i != len(timestamp)-1:
            keytimes_code  += "; "
            keypoints_code += "; "

    # Replace svg template
    output = output.replace("$TRAJECTORY$"   , svg_path_code)
    output = output.replace("$VIEWBOX$"      , viewbox_code)
    output = output.replace("$WIDTH$"        , str(viewbox_width))
    output = output.replace("$HEIGHT$"       , str(viewbox_height))
    output = output.replace("$SIMTIME$"      , str(SIM_TIME/FF_SCALE))
    # output = output.replace("$KEYTIMES$"     , keytimes_code)
    # output = output.replace("$KEYPOINTS$"    , keypoints_code)

    # Output svg data
    svg_output = open(outputpath, 'w')
    svg_output.write(output)
    svg_output.close()