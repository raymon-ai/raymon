from raymon.profiling import InputComponent, OutputComponent, ActualComponent, EvalComponent, Score

CTYPE_PRIORITY = [EvalComponent, ActualComponent, OutputComponent, InputComponent]


def find_score_ctype(profile, score):
    best_pos = len(CTYPE_PRIORITY)
    for input in score.inputs:
        input_comp = profile.components[input]
        input_ctype = type(input_comp)
        pos = CTYPE_PRIORITY.index(input_ctype)
        if pos < best_pos:
            best_pos = pos
    return CTYPE_PRIORITY[best_pos]


def get_ctype_scores(profile, ctype):
    # Get scores associated with a component type. Scores are associated with the highes component type of its inputs.
    matched_scores = []
    for score in profile.scores.values():
        score_ctype = find_score_ctype(profile, score)
        if score_ctype == ctype:
            matched_scores.append(score)
    return matched_scores


def get_ctype_components(profile, ctype, main=None):
    if main is None:
        return [c for c in profile.components.values() if isinstance(c, ctype)]
    else:
        return [c for c in profile.components.values() if isinstance(c, ctype) and c.main is main]


# Get score drops, for all component types in order
def get_score_issues(ref_profile, obs_profile, contrast_report):
    issues = []
    for ctype in CTYPE_PRIORITY:
        ctype_scores = get_ctype_scores(ref_profile, ctype)
        for score in ctype_scores:
            print(score.name)
            metrics = contrast_report["global_reports"]["scores"][score.name]
            issue = {
                "component_type": str(ctype.__name__),
                "main_component": False,  # Always False for score issues -- no hierarchy here
                "tag": None,
                "score_tags": score.inputs,
                "score": score.name,
                "issue_type": "score_regression",
                "valid": metrics["valid"],  # Set in profile
                "threshold_alert": metrics["alert"],  # Set in profile
                "value": metrics["diff"],  # Set in profile
                "extra": {
                    "ref": ref_profile.scores[score.name].result,
                    "obs": obs_profile.scores[score.name].result,
                    "preference": ref_profile.scores[score.name].preference,
                },
            }

            issues.append(issue)
    return issues


# Integrity issues, all component types in order
def get_integrity_issues(ref_profile, obs_profile, contrast_report, main=None):

    issues = []
    for ctype in CTYPE_PRIORITY:
        ctype_components = get_ctype_components(ref_profile, ctype, main=main)
        for comp in ctype_components:
            metrics = contrast_report["component_reports"][comp.name]["invalids"]
            issue = {
                "component_type": str(ctype.__name__),
                "main_component": main,  # Always False for score issues -- no hierarchy here
                "tag": comp.name,
                "score_tags": None,
                "score": None,
                "issue_type": "integrity_regression",
                "valid": metrics["valid"],  # Set in profile
                "threshold_alert": metrics["alert"],  # Set in profile
                "value": metrics["invalids"],  # Set in profile
                "extra": {
                    "ref": ref_profile.components[comp.name].stats.to_jcr(),
                    "obs": obs_profile.components[comp.name].stats.to_jcr(),
                },
            }

            issues.append(issue)
    return issues


def get_singleton_issues(ref_profile, obs_profile, contrast_report, main=None):

    issues = []
    for ctype in CTYPE_PRIORITY:
        ctype_components = get_ctype_components(ref_profile, ctype, main=main)
        for comp in ctype_components:
            metrics = contrast_report["component_reports"][comp.name]["singleton"]
            issue = {
                "component_type": str(ctype.__name__),
                "main_component": main,  # Always False for score issues -- no hierarchy here
                "tag": comp.name,
                "score_tags": None,
                "score": None,
                "issue_type": "singleton_domain",
                "valid": metrics["valid"],  # Set in profile
                "threshold_alert": metrics["alert"],  # Set in profile
                "value": int(metrics["is_singleton"]),  # Set in profile
                "extra": {
                    "ref": ref_profile.components[comp.name].stats.to_jcr(),
                    "obs": obs_profile.components[comp.name].stats.to_jcr(),
                },
            }

            issues.append(issue)
    return issues


def get_global_drift_issues(ref_profile, obs_profile, contrast_report):
    metrics = contrast_report["global_reports"]["multivariate_drift"]
    issue = {
        "component_type": None,
        "main_component": False,  # Always False for score issues -- no hierarchy here
        "tag": None,
        "score_tags": None,
        "score": None,
        "issue_type": "global_drift",
        "valid": metrics["valid"],  # Set in profile
        "threshold_alert": metrics["alert"],  # Set in profile
        "value": metrics["drift"],  # Set in profile
        "extra": {},
    }
    return [issue]


def get_drift_issues(ref_profile, obs_profile, contrast_report, main=None):

    issues = []
    for ctype in CTYPE_PRIORITY:
        ctype_components = get_ctype_components(ref_profile, ctype, main=main)
        for comp in ctype_components:
            metrics = contrast_report["component_reports"][comp.name]["drift"]
            issue = {
                "component_type": str(ctype.__name__),
                "main_component": main,  # Always False for score issues -- no hierarchy here
                "tag": comp.name,
                "score_tags": None,
                "score": None,
                "issue_type": "component_drift",
                "valid": metrics["valid"],  # Set in profile
                "threshold_alert": metrics["alert"],  # Set in profile
                "value": int(metrics["drift"]),  # Set in profile
                "extra": {
                    "ref": ref_profile.components[comp.name].stats.to_jcr(),
                    "obs": obs_profile.components[comp.name].stats.to_jcr(),
                },
            }
            issues.append(issue)
    return issues


#%%
def parse_issues(ref_profile, obs_profile, contrast_report):
    # Score issues
    score_issues = get_score_issues(
        ref_profile=ref_profile,
        obs_profile=obs_profile,
        contrast_report=contrast_report,
    )

    # Integrity issues
    main_int_issues = get_integrity_issues(
        ref_profile=ref_profile, obs_profile=obs_profile, contrast_report=contrast_report, main=True
    )
    nonmain_int_issues = get_integrity_issues(
        ref_profile=ref_profile, obs_profile=obs_profile, contrast_report=contrast_report, main=False
    )

    # Singleton issues, for all component types in order
    main_ston_issues = get_singleton_issues(
        ref_profile=ref_profile, obs_profile=obs_profile, contrast_report=contrast_report, main=True
    )
    nonmain_ston_issues = get_singleton_issues(
        ref_profile=ref_profile, obs_profile=obs_profile, contrast_report=contrast_report, main=False
    )
    # Global drift issue
    globdrift = get_global_drift_issues(
        ref_profile=ref_profile,
        obs_profile=obs_profile,
        contrast_report=contrast_report,
    )
    # other component drift issues, for all component types in order
    main_drift_issues = get_drift_issues(
        ref_profile=ref_profile, obs_profile=obs_profile, contrast_report=contrast_report, main=True
    )
    nonmain_drift_issues = get_drift_issues(
        ref_profile=ref_profile, obs_profile=obs_profile, contrast_report=contrast_report, main=False
    )
    # Now append them in order
    issues = (
        score_issues
        + main_int_issues
        + nonmain_int_issues
        + main_ston_issues
        + nonmain_ston_issues
        + globdrift
        + main_drift_issues
        + nonmain_drift_issues
    )
    return issues
