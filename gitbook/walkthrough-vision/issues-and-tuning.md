# Issues & Tuning

## Issues

After we've pushed data to Raymon, we can have a look at the Issues page on the web UI. It should look like the screenshot below. It may be pretty hectic at first sight, but as we'll see, we can easily filter through issues.&#x20;

![](<../.gitbook/assets/image (17) (1).png>)

The green labels indicate the slice with which an issue is detected. Here, we've detected issues for the global slice and for slices with a certain machine\_id. Most of them are about rather small deviations and should probably be muted (see further down below). However, others are about big deviations (e.g. 39% score regression for data coming from `machine_id==2f930ab2-3e8a-4869-a157-1bc5cd327244`) and deserve further inspection.

As outlined in [issues](issues-and-tuning.md#issues), Raymon detects issues of various types, and prioritises those. The issues with red left borders are the highest priority issues detected for a certain slice.&#x20;

## Tuning issues

Some issues are about small deviations. In some cases, it may be important to dig deeper in those too, but let's assume this is not the case here and we want to mute these issues. An example of this is the following one:

![In this case, we don't care about small performance deviations](<../.gitbook/assets/image (24).png>)

To mute an issue, click in the bell icon and a popup window will appear. In the popup window you can specify when you want to be alerted of an issue like this for this slice.

![](<../.gitbook/assets/image (18).png>)

The first field allows you to tune the magnitude of the issue. The last 2 fields allow you to to specify how often out of the last how many checks the check leading to this issue should exceed the threshold in order for the issue to be raised. Let's use the defaults and press OK here.&#x20;

## Filtering Issues

To make more sense out of the issues that are shown, we can filter them using the filter box shown at the top of the page. let's look a bit closer into the slice leading to the big score regression. Paste `machine_id==2f930ab2-3e8a-4869-a157-1bc5cd327244 `into the "Show only for slice: field and press filter. Now, you will only see issues related to that slice, in order of priority.

![](<../.gitbook/assets/image (17).png>)

We immediately see that all scores associated with this slice (the first 3 issues) have serious regressions. Below these, we see integrity regressions for input features, which means they have "invalid" values. More specifically, it seems that 85% of the traces in this slice has an invalid sharpness, and 96% has an invalid outlier score. How come? Let's click on the issue for more information!

![Detail view of the outlier score integrity regression issue. Blue = data in the current slice, red = data in the global population.](<../.gitbook/assets/image (23).png>)

When looking at the Tag distribution, we see that the current slice clearly has a different distribution than the global population (which aligns rather nicely with the profile we built before). From the Tag Error distribution we can deduct that this leads to UpperBoundErrors. Thus, the outlier scores are much higher than those seen during profile building, leading to them to be seen as invalid values.

We can now go to the dashboards and create a scatterplot for the outlier score tag. This shows us the same info as before, but presented differently. The nice thing here is that this scatterplot is clickable though. By clicking on one of the red dots, we can jumpy directly to the trace for that dot.

![](<../.gitbook/assets/image (22).png>)

After clicking some of the red dots, scrolling through the trace, and comparing it with the traces from the blue dots, it should become clear what is wrong. The camera with id `2f930ab2-3e8a-4869-a157-1bc5cd327244` clearly produces blurry images and someone should take a look at it.

![This image is obviously too blurry to make a prediction on.](<../.gitbook/assets/image (21).png>)

If you're wondering how this can be: we programmed it like this for this demo ([here](https://github.com/raymon-ai/raymon-demos/blob/96639ee4a40bc346d8cb34963dfc7de41a283826/retinopathy/retinopathy/base\_raymon\_actuals.py#L118)), but real diabetic retinopathy detection is of course also susceptible to regressions due to faulty or novel data, as mentioned [here](https://research.google/pubs/pub49953.pdf) (page 2, 2nd paragraph) and [here](https://www.theguardian.com/technology/2021/oct/20/ai-projects-to-tackle-racial-inequality-in-uk-healthcare-says-javid) (about halfway through) for example.

## Wrap-up

In this walkthrough we've seen how we can integrate Raymon and set up monitoring with it. We have not touched everything, so feel free to explore further. All questions and suggestions are most welcome at [hello@raymon.ai](mailto:hello@raymon.ai).&#x20;
