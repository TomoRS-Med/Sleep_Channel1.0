"""Readable equations for the supported paper-derived neuron models."""
from paper_catalog import get_model, validate_disabled_channels


CHANNELS = {
    "leak": """Leak current
I_L = gL(V − VL)""",
    "nan_leak": """Leak and NALCN sodium component
I_leak = gLeak(V − VL)
gLeNa = gLeak(VL − VK)/(VLeNa − VK)
I_Na,NALCN = 0.44 gLeNa(V − VNa)""",
    "na": """Fast voltage-gated NaV current
I_Na = gNa mNa∞³ hNa(V − VNa)
mNa∞ = αm/(αm + βm)
αm = 0.1(V + 33)/[1 − exp(−(V + 33)/10)]
βm = 4 exp(−(V + 53.7)/12)
dhNa/dt = 4[αh(1 − hNa) − βh hNa]
αh = 0.07 exp(−(V + 50)/10)
βh = 1/[1 + exp(−(V + 20)/10)]""",
    "unav": """Shifted UNaV current
I_UNaV = gUNaV mUNaV∞³ hUNaV(V − VNa)
mUNaV∞ = αm'/(αm' + βm')
αm' = 0.1(V + 33 + x)/[1 − exp(−(V + 33 + x)/10)]
βm' = 4 exp(−(V + 53.7 + x)/12)
dhUNaV/dt = 4[αh'(1 − hUNaV) − βh' hUNaV]
αh' = 0.07 exp(−(V + 50 + y)/10)
βh' = 1/[1 + exp(−(V + 20 + y)/10)]""",
    "kv": """Delayed-rectifier K current
I_K = gK nK⁴(V − VK)
dnK/dt = 4[αn(1 − nK) − βn nK]
αn = 0.01(V + 34)/[1 − exp(−(V + 34)/10)]
βn = 0.125 exp(−(V + 44)/25)""",
    "kna": """Sodium-dependent KNa current
I_KNa = gKNa mKNa∞(V − VK)
mKNa∞ = 1/[1 + (Ke/[Na])^Kf]""",
    "a": """A-type K current
I_A = gA mA∞³ hA(V − VK)
mA∞ = 1/[1 + exp(−(V + 50)/20)]
dhA/dt = (hA∞ − hA)/τhA
hA∞ = 1/[1 + exp((V + 80)/6)]""",
    "a_fnan": """A-type K current (FNAN activation curve)
I_A = gA mA∞³ hA(V − VK)
mA∞ = 1/[1 + exp(−(V + 44)/50)]
dhA/dt = (hA∞ − hA)/τhA
hA∞ = 1/[1 + exp((V + 80)/6)]""",
    "ks": """Slow K current
I_KS = gKS mKS(V − VK)
dmKS/dt = (mKS∞ − mKS)/τmKS
mKS∞ = 1/[1 + exp(−(V + 34)/6.5)]
τmKS = 8/[exp(−(V + 55)/30) + exp((V + 55)/30)]""",
    "ca": """Voltage-gated Ca current
I_Ca = gCa mCa∞²(V − VCa)
mCa∞ = 1/[1 + exp(−(V + 20)/9)]""",
    "kca": """Calcium-dependent KCa current
I_KCa = gKCa mKCa∞(V − VK)
mKCa∞ = 1/[1 + (Kd/[Ca])³·⁵]""",
    "nap": """Persistent NaP current
I_NaP = gNaP mNaP∞³(V − VNa)
mNaP∞ = 1/[1 + exp(−(V + 55.7)/7.7)]""",
    "ar": """Inward-rectifier K current
I_AR = gAR hAR∞(V − VK)
hAR∞ = 1/[1 + exp((V + 75)/4)]""",
    "ampa": """AMPA synaptic current
I_AMPA = gAMPA sAMPA(V − VAMPA)
f(V) = 1/[1 + exp(−(V − 20)/2)]
dsAMPA/dt = 3.48 f(V) − sAMPA/τAMPA""",
    "nmda": """NMDA synaptic current
I_NMDA = gNMDA sNMDA(V − VNMDA)
dsNMDA/dt = 0.5 xNMDA(1 − sNMDA) − sNMDA/τsNMDA
dxNMDA/dt = 3.48 f(V) − xNMDA/τxNMDA""",
    "gaba": """GABA synaptic current
I_GABA = gGABA sGABA(V − VGABA)
dsGABA/dt = f(V) − sGABA/τGABA""",
}

CHANNEL_PARAMETER = {
    "leak": "gL", "nan_leak": "gLeak", "na": "gNa", "unav": "gUNaV",
    "kv": "gK", "kna": "gKNa", "a": "gA", "a_fnan": "gA",
    "ks": "gKS", "ca": "gCa", "kca": "gKCa", "nap": "gNaP",
    "ar": "gAR", "ampa": "gAMPA", "nmda": "gNMDA", "gaba": "gGABA",
}


def equations_for(model_name, disabled_channels=()):
    """Return only the currents and gates active in the selected model."""
    spec = get_model(model_name)
    disabled = set(validate_disabled_channels(model_name, disabled_channels))
    family = spec["family"]
    if family == "AN":
        membrane = ("C A dV/dt = −A(I_L + I_Na + I_K + I_A + I_KS + I_Ca + "
                    "I_KCa + I_NaP + I_AR) − I_AMPA − I_NMDA − I_GABA")
        ions = "d[Ca]/dt = −αCa(10A I_Ca + I_NMDA) − [Ca]/τCa"
        active = ("leak", "na", "kv", "a", "ks", "ca", "kca", "nap", "ar",
                  "ampa", "nmda", "gaba")
    elif family in ("SAN", "RAN"):
        potassium = "I_K" if family == "SAN" else "I_KS"
        membrane = f"C dV/dt = −(I_L + I_NaP + {potassium} + I_Ca + I_KCa)"
        ions = "d[Ca]/dt = −αCa(10A I_Ca) − [Ca]/τCa"
        active = ("leak", "nap", "kv" if family == "SAN" else "ks", "ca", "kca")
    elif family == "NAN":
        membrane = "C dV/dt = −(I_leak + I_K + I_UNaV + I_KNa + I_Ca)"
        ions = ("d[Na]/dt = {−αNa(10A)(I_UNaV + I_Na,NALCN) "
                "− 1000[Na]/τNa}/1000\n[Ca] is not a dynamic state in NAN.")
        active = ("nan_leak", "unav", "kv", "kna", "ca")
    elif family == "FNAN":
        membrane = ("C A dV/dt = −A(I_leak + I_K + I_UNaV + I_KNa + I_Ca + "
                    "I_Na + I_A + I_KS + I_KCa + I_NaP + I_AR) "
                    "− I_AMPA − I_NMDA − I_GABA")
        ions = ("d[Na]/dt = {−αNa(10A)(I_Na + I_NaP + I_UNaV + I_Na,NALCN) "
                "− 1000[Na]/τNa}/1000\n"
                "d[Ca]/dt = −αCa(10A)(I_Ca + I_Ca,NALCN) − [Ca]/τCa\n"
                "I_Ca,NALCN = 0.25 gLeNa(V − VCa)")
        active = ("nan_leak", "unav", "kv", "kna", "ca", "na", "a_fnan",
                  "ks", "kca", "nap", "ar", "ampa", "nmda", "gaba")
    else:
        raise ValueError("No equations for " + model_name)
    channel_sections = []
    for name in active:
        key = CHANNEL_PARAMETER[name]
        if key in disabled:
            title = CHANNELS[name].splitlines()[0]
            channel_sections.append(f"{title} — OFF\n{key} = 0; this current is zero.")
        else:
            channel_sections.append(CHANNELS[name])
    sections = [f"{model_name}  |  {spec['equations']}",
                "MEMBRANE POTENTIAL\n" + membrane,
                "ION CONCENTRATION\n" + ions,
                *channel_sections,
                "Units: V in mV, time in ms, A in mm². Intrinsic currents are "
                "µA/cm²; synaptic currents are nA. The density-to-nA factor is 10A. "
                "At removable 0/0 points, activation rates use their analytic limits."]
    return "\n\n".join(sections)
