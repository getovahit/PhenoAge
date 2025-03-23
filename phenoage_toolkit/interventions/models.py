class InterventionModels:
    """
    Models for various lifestyle and supplement interventions that can affect biomarkers.
    Each intervention method takes biomarker data and returns updated biomarker values.
    """
    
    @staticmethod
    def clamp(val, minv, maxv=None):
        """
        Utility function to clamp a value between minimum and maximum values
        
        Parameters:
        -----------
        val : float
            Value to clamp
        minv : float
            Minimum allowed value
        maxv : float, optional
            Maximum allowed value (default: None)
            
        Returns:
        --------
        float
            Clamped value
        """
        if val < minv:
            return minv
        if maxv is not None and val > maxv:
            return maxv
        return val

    @classmethod
    def apply_exercise(cls, biomarkers):
        """
        Regular Exercise: lowers CRP significantly if CRP is high, lowers Glucose,
        can reduce WBC if elevated, can bump lymphocyte%, etc.
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        
        # hsCRP logic (from references: can drop CRP by ~6–8 mg/L in overweight w/ high CRP)
        crp = new_vals["crp"]
        if crp >= 3.0:
            # large drop, e.g. ~3 mg/L
            new_vals["crp"] = cls.clamp(crp - 3.0, 0.01)
        elif crp >= 1.0:
            # moderate drop
            new_vals["crp"] = cls.clamp(crp - 1.0, 0.01)
        else:
            # if CRP <1, small drop
            new_vals["crp"] = cls.clamp(crp - 0.2, 0.01)
        
        # Glucose: ~5–15 mg/dL drop, bigger if baseline is high
        glu = new_vals["glucose"]
        if glu >= 130:
            new_vals["glucose"] = cls.clamp(glu - 15, 70)
        elif glu >= 100:
            new_vals["glucose"] = cls.clamp(glu - 7, 70)
        else:
            new_vals["glucose"] = cls.clamp(glu - 3, 70)
        
        # WBC: if high, reduce by 1.0
        wbc = new_vals["wbc"]
        if wbc >= 8.0:
            new_vals["wbc"] = max(wbc - 1.0, 4.0)
        
        # Lymphocyte%: might rise a few points if it was low
        lymph = new_vals["lymphocyte"]
        if lymph < 30:
            new_vals["lymphocyte"] = cls.clamp(lymph + 5, 5, 60)
        else:
            new_vals["lymphocyte"] = lymph  # no big effect if already normal

        return new_vals

    @classmethod
    def apply_weight_loss(cls, biomarkers):
        """
        Weight Loss: ~10% body weight loss => 30–40% CRP drop, 5–20 mg/dL glucose drop, lowers WBC, etc.
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        
        # CRP
        crp = new_vals["crp"]
        # If CRP is e.g. 4 mg/L => 30–40% => ~1.5 mg/L drop. We'll do piecewise:
        if crp >= 5.0:
            new_vals["crp"] = cls.clamp(crp - 2.0, 0.01)
        elif crp >= 2.0:
            new_vals["crp"] = cls.clamp(crp - 1.0, 0.01)
        else:
            new_vals["crp"] = cls.clamp(crp - 0.2, 0.01)
        
        # Glucose
        glu = new_vals["glucose"]
        if glu >= 130:
            new_vals["glucose"] = cls.clamp(glu - 20, 70)
        elif glu >= 100:
            new_vals["glucose"] = cls.clamp(glu - 10, 70)
        else:
            new_vals["glucose"] = cls.clamp(glu - 3, 70)
        
        # WBC if high
        wbc = new_vals["wbc"]
        if wbc > 7.5:
            new_vals["wbc"] = max(wbc - 1.0, 4.0)
        
        return new_vals

    @classmethod
    def apply_low_allergen_diet(cls, biomarkers):
        """
        Low-Allergen / Anti-Inflammatory Diet:
        CRP can drop ~0.2–0.5 mg/L if mild, more if truly inflamed.
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        crp = new_vals["crp"]
        if crp >= 3.0:
            new_vals["crp"] = cls.clamp(crp - 1.0, 0.01)
        elif crp >= 1.0:
            new_vals["crp"] = cls.clamp(crp - 0.5, 0.01)
        else:
            new_vals["crp"] = cls.clamp(crp - 0.2, 0.01)
        return new_vals

    @classmethod
    def apply_curcumin(cls, biomarkers):
        """
        Curcumin (500–1000 mg/day):
        Lowers CRP by ~3.7 mg/L if CRP is high, or ~0.3 mg/L if low
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        crp = new_vals["crp"]
        if crp >= 3.0:
            new_vals["crp"] = cls.clamp(crp - 3.7, 0.01)
        elif crp >= 1.0:
            new_vals["crp"] = cls.clamp(crp - 1.0, 0.01)
        else:
            # already quite low => maybe 0.2 mg/L
            new_vals["crp"] = cls.clamp(crp - 0.2, 0.01)
        return new_vals

    @classmethod
    def apply_omega3(cls, biomarkers):
        """
        Omega-3 (1.5–3 g/day):
        CRP down ~2–3 mg/L if CRP is high (>=5). If CRP <1, maybe ~0.3 mg/L.
        Also can reduce WBC if it's high. Might raise lymph% a bit.
        Albumin can slightly rise in inflammatory states.
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        crp = new_vals["crp"]
        if crp >= 5.0:
            new_vals["crp"] = cls.clamp(crp - 3.0, 0.01)
        elif crp >= 1.0:
            new_vals["crp"] = cls.clamp(crp - 1.0, 0.01)
        else:
            new_vals["crp"] = cls.clamp(crp - 0.3, 0.01)
        
        wbc = new_vals["wbc"]
        if wbc >= 8.0:
            new_vals["wbc"] = max(wbc - 0.8, 4.0)
        
        # If albumin <4.0 and cause is inflammation, might raise it ~0.2
        albumin = new_vals["albumin"]
        if albumin < 4.0:
            new_vals["albumin"] = min(albumin + 0.2, 5.0)

        # Might raise lymph% if it was low
        lymph = new_vals["lymphocyte"]
        if lymph < 30:
            new_vals["lymphocyte"] = cls.clamp(lymph + 3, 5, 60)
        
        return new_vals

    @classmethod
    def apply_taurine(cls, biomarkers):
        """
        Taurine (3–6 g/day):
        ~16–29% CRP drop in diabetics, let's do ~0.4 mg/L if CRP moderate.
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        crp = new_vals["crp"]
        if crp >= 3.0:
            new_vals["crp"] = cls.clamp(crp - 1.0, 0.01)
        elif crp >= 1.0:
            new_vals["crp"] = cls.clamp(crp - 0.4, 0.01)
        else:
            new_vals["crp"] = cls.clamp(crp - 0.1, 0.01)
        return new_vals

    @classmethod
    def apply_high_protein_diet(cls, biomarkers):
        """
        High Protein Intake: raises albumin by 0.2–0.5 g/dL if albumin is low (<4.0).
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        alb = new_vals["albumin"]
        if alb < 4.0:
            # raise by e.g. 0.3
            new_vals["albumin"] = min(alb + 0.3, 5.0)
        return new_vals

    @classmethod
    def apply_reduce_alcohol(cls, biomarkers):
        """
        Reduce Alcohol:
        Can raise albumin if it was low, can lower ALP if it was high.
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        alb = new_vals["albumin"]
        alp = new_vals["alkaline_phosphatase"]
        
        # If albumin <4 => can rebound by ~0.5
        if alb < 4.0:
            new_vals["albumin"] = min(alb + 0.5, 5.0)
        
        # If ALP >120 => can drop 20–60
        if alp > 120:
            new_vals["alkaline_phosphatase"] = max(alp - 40, 50)
        elif alp > 100:
            new_vals["alkaline_phosphatase"] = max(alp - 20, 50)
        
        return new_vals

    @classmethod
    def apply_stop_creatine(cls, biomarkers):
        """
        Stop Creatine Supplementation:
        Lowers creatinine by ~0.2–0.3 mg/dL if user was taking it.
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        creat = new_vals["creatinine"]
        new_vals["creatinine"] = max(creat - 0.25, 0.6)
        return new_vals

    @classmethod
    def apply_reduce_red_meat(cls, biomarkers):
        """
        Reduce Red Meat Intake:
        Can lower creatinine by ~0.1–0.4 mg/dL
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        creat = new_vals["creatinine"]
        # if quite high => bigger drop
        if creat >= 1.2:
            new_vals["creatinine"] = max(creat - 0.3, 0.6)
        else:
            new_vals["creatinine"] = max(creat - 0.1, 0.6)
        return new_vals

    @classmethod
    def apply_reduce_sodium(cls, biomarkers):
        """
        Reduce Sodium:
        Might improve creatinine by 0.1–0.2 mg/dL in borderline CKD
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        creat = new_vals["creatinine"]
        if creat >= 1.2:
            new_vals["creatinine"] = max(creat - 0.2, 0.6)
        else:
            new_vals["creatinine"] = max(creat - 0.1, 0.6)
        return new_vals

    @classmethod
    def apply_avoid_nsaids(cls, biomarkers):
        """
        Avoid NSAIDs:
        Can reduce creatinine by ~0.1–0.3 mg/dL if it was elevated from NSAIDs.
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        creat = new_vals["creatinine"]
        new_vals["creatinine"] = max(creat - 0.2, 0.6)
        return new_vals

    @classmethod
    def apply_avoid_heavy_exercise(cls, biomarkers):
        """
        Avoid Very Heavy Exercise Before Testing:
        May lower ALP by ~10–15% if it was elevated from bone isoenzyme.
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        alp = new_vals["alkaline_phosphatase"]
        # If ALP > 100 => drop ~15%
        if alp > 100:
            new_vals["alkaline_phosphatase"] = max(alp * 0.85, 50)
        else:
            # small drop
            new_vals["alkaline_phosphatase"] = max(alp - 5, 30)
        return new_vals

    @classmethod
    def apply_milk_thistle(cls, biomarkers):
        """
        Milk Thistle (1 g/day):
        Reduces ALP by 20–40 U/L if elevated.
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        alp = new_vals["alkaline_phosphatase"]
        if alp >= 130:
            new_vals["alkaline_phosphatase"] = max(alp - 30, 50)
        elif alp >= 100:
            new_vals["alkaline_phosphatase"] = max(alp - 20, 50)
        return new_vals

    @classmethod
    def apply_nac(cls, biomarkers):
        """
        NAC (1–2 g/day):
        Might lower ALP by 5–15% if elevated.
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        alp = new_vals["alkaline_phosphatase"]
        if alp >= 120:
            new_vals["alkaline_phosphatase"] = max(alp * 0.85, 50)
        elif alp >= 100:
            new_vals["alkaline_phosphatase"] = max(alp * 0.90, 50)
        return new_vals

    @classmethod
    def apply_carb_fat_restriction(cls, biomarkers):
        """
        Carb & Fat Restriction => 5–20 mg/dL glucose reduction if baseline is high
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        glu = new_vals["glucose"]
        if glu >= 130:
            new_vals["glucose"] = cls.clamp(glu - 15, 70)
        elif glu >= 100:
            new_vals["glucose"] = cls.clamp(glu - 10, 70)
        else:
            new_vals["glucose"] = cls.clamp(glu - 3, 70)
        return new_vals

    @classmethod
    def apply_postmeal_walk(cls, biomarkers):
        """
        Walking After Meals => small effect on fasting glucose (maybe 2–5 mg/dL)
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        glu = new_vals["glucose"]
        if glu > 100:
            new_vals["glucose"] = cls.clamp(glu - 5, 70)
        else:
            new_vals["glucose"] = cls.clamp(glu - 2, 70)
        return new_vals

    @classmethod
    def apply_sauna(cls, biomarkers):
        """
        Sauna => mild lowering of glucose (2–5 mg/dL), 
                 raises WBC & lymphocyte% short term, can help if low
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        # Glucose
        glu = new_vals["glucose"]
        new_vals["glucose"] = cls.clamp(glu - 4, 70)

        # WBC: if low, might raise; if normal/high, no big change
        wbc = new_vals["wbc"]
        if wbc < 4.0:
            new_vals["wbc"] = wbc + 0.5  # mild bump
        # Lymphocyte: if <30, might raise it
        lymph = new_vals["lymphocyte"]
        if lymph < 30:
            new_vals["lymphocyte"] = cls.clamp(lymph + 5, 5, 60)
        return new_vals

    @classmethod
    def apply_berberine(cls, biomarkers):
        """
        Berberine (500–1000 mg/day):
        Lowers glucose by ~10–20 mg/dL if diabetic, smaller if borderline
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        glu = new_vals["glucose"]
        if glu >= 130:
            new_vals["glucose"] = cls.clamp(glu - 15, 70)
        elif glu >= 100:
            new_vals["glucose"] = cls.clamp(glu - 10, 70)
        else:
            new_vals["glucose"] = cls.clamp(glu - 3, 70)
        return new_vals

    @classmethod
    def apply_vitb1(cls, biomarkers):
        """
        Vitamin B1 (Thiamine ~100 mg/day):
        If user is borderline high glucose, might drop ~5 mg/dL
        If truly high, maybe 10 mg/dL
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        glu = new_vals["glucose"]
        if glu >= 130:
            new_vals["glucose"] = cls.clamp(glu - 10, 70)
        elif glu >= 100:
            new_vals["glucose"] = cls.clamp(glu - 5, 70)
        return new_vals

    @classmethod
    def apply_olive_oil(cls, biomarkers):
        """
        Olive Oil (Mediterranean):
        Slightly lowers neutrophils => raises lymph% a bit if was low
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        lymph = new_vals["lymphocyte"]
        if lymph < 35:
            new_vals["lymphocyte"] = cls.clamp(lymph + 3, 5, 60)
        return new_vals

    @classmethod
    def apply_mushrooms(cls, biomarkers):
        """
        Mushrooms: can raise lymphocyte% by up to ~5–10 points if low
        Also can raise WBC if low.
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        lymph = new_vals["lymphocyte"]
        if lymph < 35:
            new_vals["lymphocyte"] = cls.clamp(lymph + 7, 5, 60)
        
        wbc = new_vals["wbc"]
        if wbc < 4.0:
            new_vals["wbc"] = wbc + 0.8
        return new_vals

    @classmethod
    def apply_zinc(cls, biomarkers):
        """
        Zinc: If user has low lymphocytes or WBC, can raise them somewhat
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        wbc = new_vals["wbc"]
        if wbc < 4.0:
            new_vals["wbc"] = wbc + 0.5
        
        lymph = new_vals["lymphocyte"]
        if lymph < 30:
            new_vals["lymphocyte"] = cls.clamp(lymph + 5, 5, 60)
        return new_vals

    @classmethod
    def apply_bcomplex(cls, biomarkers):
        """
        B-Complex: can fix elevated RDW from B12/folate deficiency,
        and can fix high MCV if macrocytic.
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        rdw = new_vals["rdw"]
        if rdw >= 18.0:
            # big drop to normal
            new_vals["rdw"] = 14.0
        elif rdw >= 15.0:
            new_vals["rdw"] = 13.5
        
        mcv = new_vals["mcv"]
        if mcv >= 100:
            new_vals["mcv"] = max(mcv - 10, 80)  # drop ~10 fL
        return new_vals

    @classmethod
    def apply_balanced_diet(cls, biomarkers):
        """
        Well-Balanced Diet: helps albumin if malnourished, helps MCV if micro/macro,
        small CRP improvement, etc.
        
        Parameters:
        -----------
        biomarkers : dict
            Dictionary of biomarker values
            
        Returns:
        --------
        dict
            Updated biomarkers after intervention
        """
        new_vals = biomarkers.copy()
        # albumin
        alb = new_vals["albumin"]
        if alb < 4.0:
            new_vals["albumin"] = min(alb + 0.5, 5.0)
        
        # MCV: if out of range, nudge toward normal
        mcv = new_vals["mcv"]
        if mcv < 80:
            new_vals["mcv"] = min(mcv + 5, 80)
        elif mcv > 100:
            new_vals["mcv"] = max(mcv - 5, 100)
        
        # CRP small improvement
        crp = new_vals["crp"]
        new_vals["crp"] = cls.clamp(crp - 0.3, 0.01)
        
        return new_vals
