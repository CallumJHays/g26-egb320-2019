def OmniAdj(left,right,back):
        Vs = 3 #self.Vs
        Mx_Motor = 3.5 #self.Speed
        thresh = 1.2 #self.Thresh
        floor = thresh/(Mx_Motor/Vs)
        motMIN = max(0.0001,left,right,back)
        if thresh > motMIN:
            factor = motMIN
        else:
            factor = floor
        
        adjust = min(Mx_Motor/Vs,floor/factor)
        Left_PWM = adjust*left
        Right_PWM = adjust*right
        Back_PWM = adjust*back