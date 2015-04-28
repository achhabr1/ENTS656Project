'''
Created on May 2, 2014

@author: Ankit
'''
import numpy as ny
import random as rnd

def simulationRun(no_of_call_per_hour):
    
    iteration_time = 3600
    probability = no_of_call_per_hour/3600
    total_MS = 150
    transmit_power = 20
    line_loss = 4
    antenna_gain = 8
    frequency_BS0 = 900
    frequency_BS1 = 905
    RSL_threshold = -102
    BS0_channels = 15
    BS1_channels = 15
    counter_BS0_channels = 0
    counter_BS1_channels = 0
    margin_handoff = 3
    call_attempts_BS0 = 0
    call_attempts_BS1 = 0
    call_block_lack_signal_strength_BS0 = 0
    call_block_lack_signal_strength_BS1 = 0
    call_block_lack_capacity_BS0 = 0
    call_block_lack_capacity_BS1 = 0
    call_dropped_lack_signal_strength_BS0 = 0
    call_dropped_lack_signal_strength_BS1 = 0
    call_handoff_failures_BS0 = 0
    call_handoff_failures_BS1 = 0
    call_successfull_handoffs_BS0 = 0
    call_successfull_handoffs_BS1 = 0
    call_completed_sucessfully_BS0 = 0
    call_completed_sucessfully_BS1 = 0
    total_time_call_up_BS0 = 0
    total_time_call_up_BS1 = 0
    call_duration = 180
    mobile_appearance_rate = 0.5
    new_mobile_initial_sr_no = 1000
    GOS_BS0 = 0
    GOS_BS1 = 0
    handoff_failure_rate_BS0 = 0
    handoff_failure_rate_BS1 = 0
    traffic_intensity_BS0 = 0
    traffic_intensity_BS1 = 0
    # generation of 150 MS in 0-6KM distance range
    MS = ny.random.uniform(0,6,total_MS)
    
    #deciding directions of Mobile Stations
    dir_id_set = ny.random.randint(2,size = total_MS)
    
    final_direction_set = []
    
    for i in dir_id_set:
        if i == 0:
            final_direction_set.append(-0.01) # going west
        else:
            final_direction_set.append(0.01) # going east
    
    # calculating distances from respective Base Stations
    def distance_BS0(X):
        distance_BS0 = ny.sqrt((X-1.5)**2+0.1**2)
        return(distance_BS0)
    
    def distance_BS1(X):
        distance_BS1 = ny.sqrt((X-4.5)**2+0.1**2)
        return(distance_BS1)
    
    #RSL function
    def RSL(fc,distance):
    
        mobile_height = 1.50
        antenna_height = 30
        
        # transmit powern in db
        transmit_power_db = 10*ny.log10(transmit_power/0.001)
    
        # function to calculate propagation loss using Okamura Hata model for small city
        ahre = (1.1*ny.log10(fc)-0.7)*mobile_height-(1.56*ny.log10(fc)-0.8)
        #ahre = 0.02
        loss = 69.55 + 26.16*ny.log10(fc)- 13.82*ny.log10(antenna_height)-ahre+(44.9-6.55*ny.log10(antenna_height))*ny.log10(distance)
    
        # shadowing loss with mean = 0, std = 2 db
        shadow_loss = ny.random.normal(0,2)
    
        # Fading loss
        first_samples = ny.random.normal(0,1,4)
        second_samples = ny.random.normal(0,1,4)
        gaussian_random_complex = first_samples + 1j*second_samples
        fading_loss_values_set = 20*ny.log10(ny.abs(gaussian_random_complex))
        fading_loss_values_set.sort()
    
        EIRP = transmit_power_db-line_loss+antenna_gain
        
        #calculating Receive power level from Base Station 1&2
        rsl_BS = EIRP - loss + shadow_loss + fading_loss_values_set[1]
        
        return(rsl_BS)
    
    #Mobile parameter set initialization
    # MS_parameter_set = {'Mobile_id':[Location, Direction, RSL from BS0 , RSL from BS1, Attached Base Station, Call Status, Call Duration
    # Call Status: 0 = Down , 1 = UP, 2 = Dead Mobile (Out of Range)
    MS_parameter_set = {}
    
    # At t = 0 second:
    for i in range(len(MS)):
        
        # updating MS location in Mobile Parameters Set
        MS_parameter_set[i] = [MS[i],final_direction_set[i]]
    
        # MS distance from both base stations
        d_bs0 = distance_BS0(MS[i])
        d_bs1 = distance_BS1(MS[i]) 
        
        # Checking probability if mobile will make a call request
        if rnd.random() <= probability:
            
            #calculate RSl from BS0 & BS1
            rsl_BS0 = RSL(frequency_BS0, d_bs0)
            rsl_BS1 = RSL(frequency_BS1, d_bs1)
            MS_parameter_set[i].append (rsl_BS0)
            MS_parameter_set[i].append (rsl_BS1)
            
            if rsl_BS0 <= rsl_BS1:
                MS_parameter_set[i].append(2) # serving Base Station 1
                call_attempts_BS1 = call_attempts_BS1 + 1 #updating call attempt parameter on BS1
                MS_RSL = rsl_BS1
    
                # RSL below threshold 
                if MS_RSL < RSL_threshold:
                    MS_parameter_set[i].append(0) # Call Status
                    call_block_lack_signal_strength_BS1 = call_block_lack_signal_strength_BS1 + 1
                    
                    MS_parameter_set[i].append(0) # call duration   
                else:
    
                    if counter_BS1_channels  < BS1_channels:                  
                        counter_BS1_channels = counter_BS1_channels +1
                        MS_parameter_set[i].append(1) #call status "UP"
                        MS_parameter_set[i].append(0) #call duration
    
                    else:
    
                        call_block_lack_capacity_BS1 = call_block_lack_capacity_BS1 + 1
                        MS_parameter_set[i].append(0) #call status "Down"
                        MS_parameter_set[i].append(0) #call duration
    
            elif rsl_BS0 > rsl_BS1:
    
                MS_parameter_set[i].append(1) # serving Base Station 0
                call_attempts_BS0 = call_attempts_BS0 + 1 #updating call attempt parameter on BS0
                MS_RSL = rsl_BS0
    
                # RSL below threshold
                if MS_RSL < RSL_threshold:
                    MS_parameter_set[i].append(0) #call status "Down" 
                    call_block_lack_signal_strength_BS0 = call_block_lack_signal_strength_BS0 + 1
                    MS_parameter_set[i].append(0) #call duration
                    
                else:
                    # call assignment
                    if counter_BS0_channels  < BS0_channels:      
                        counter_BS0_channels = counter_BS0_channels +1
                        MS_parameter_set[i].append(1) #call status "UP"
                        MS_parameter_set[i].append(0) #call duration
    
                    else:
                        call_block_lack_capacity_BS0 = call_block_lack_capacity_BS0 + 1
                        MS_parameter_set[i].append(0) #call status "Down"
                        MS_parameter_set[i].append(0) #call duration
        else:
            MS_parameter_set[i].extend([0,0,0,0,0])
            
    # t = 1 to 3600 seconds:
    for i in range(1,iteration_time):    
        
        for j in MS_parameter_set:
               
            # updating MS distances with corresponding east or west directions
            MS_parameter_set[j][0] = MS_parameter_set[j][0] + MS_parameter_set[j][1]
            
            if MS_parameter_set[j][0] <= 0.0 or MS_parameter_set[j][0] >= 6.0: # Mobile moves out of specified range of 0-6KM.
                
                if MS_parameter_set[j][5] == 1: #Checking if the call was up 
                    
                    if MS_parameter_set[j][4] == 1:
                        call_successfull_handoffs_BS0 = call_successfull_handoffs_BS0 + 1 #success full hand off from BS0
                        counter_BS0_channels = counter_BS0_channels - 1 #release channel
    
                    elif MS_parameter_set[j][4] == 2:
                        call_successfull_handoffs_BS1 = call_successfull_handoffs_BS1 + 1 #success full hand off from BS1
                        counter_BS1_channels = counter_BS1_channels - 1 #release channel
                
                MS_parameter_set[j][5] = 2 # setting call status parameter "Dead Mobile"
                 
            if MS_parameter_set[j][5] == 0:
                
                # Probability if mobile will make a call request
                if rnd.random() <= probability:    
                    
                    #calculating and assigning RSL
                    d_bs0 = distance_BS0(MS_parameter_set[j][0])
                    d_bs1 = distance_BS1(MS_parameter_set[j][0])
                    
                    rsl_BS0 = RSL(frequency_BS0, d_bs0)
                    rsl_BS1 = RSL(frequency_BS1, d_bs1)
                    MS_parameter_set[j][2] = rsl_BS0
                    MS_parameter_set[j][3] = rsl_BS1
                    
                    
                    if rsl_BS0 <= rsl_BS1:
                    
                        MS_parameter_set[j][4]= 2 # serving Base Station 1
                       
                        call_attempts_BS1 = call_attempts_BS1 + 1 #updating call attempt parameter on BS1
                        MS_RSL = rsl_BS1
                        
                        # RSL below threshold 
                        if MS_RSL < RSL_threshold:
                            
                            MS_parameter_set[j][5] = 0 #Call status "Down"
                            call_block_lack_signal_strength_BS1 = call_block_lack_signal_strength_BS1 + 1
                        else:
            
                            if counter_BS1_channels  < BS1_channels:
                                
                                counter_BS1_channels = counter_BS1_channels + 1
                                MS_parameter_set[j][5] = 1 #call status "UP"
                                MS_parameter_set[j][6] = 0 #call duration
                                
                            else:
                                call_block_lack_capacity_BS1 = call_block_lack_capacity_BS1 + 1
                                MS_parameter_set[j][5] = 0 #call status "Down"
                    else: 
                       
                        MS_parameter_set[j][4] = 1 # serving Base Station 0
                        call_attempts_BS0 = call_attempts_BS0 + 1 #updating call attempt parameter on BS0
                        MS_RSL = rsl_BS0
                        
                        # RSL below threshold
                        if MS_RSL < RSL_threshold:
                            MS_parameter_set[j][5] = 0 #call status
                            call_block_lack_signal_strength_BS0 = call_block_lack_signal_strength_BS0 + 1
                                
                        else:
                            # call assignment
                            if counter_BS0_channels  < BS0_channels:
                                
                                counter_BS0_channels = counter_BS0_channels +1
                                MS_parameter_set[j][5] = 1 #call status "UP"
                                MS_parameter_set[j][6] = 0 #call duration
                                
                            else:
                                call_block_lack_capacity_BS0 = call_block_lack_capacity_BS0 + 1
                                MS_parameter_set[j][5] = 0 #call status "Down"
                    
            elif MS_parameter_set[j][5] == 1:
                
                #Incrementing call duration by one second
                MS_parameter_set[j][6] = MS_parameter_set[j][6] + 1
                
                #Total Time calculation on each Base Stations
                if MS_parameter_set[j][4] == 1:
                    total_time_call_up_BS0 = total_time_call_up_BS0 +1
                elif MS_parameter_set[j][4] == 2:
                    total_time_call_up_BS1 = total_time_call_up_BS1 +1                
                
                if MS_parameter_set[j][6] >= call_duration: 
                    
                    if MS_parameter_set[j][4] == 1:
                        counter_BS0_channels = counter_BS0_channels -1 #release channel
                        call_completed_sucessfully_BS0 = call_completed_sucessfully_BS0 + 1
                    
                    elif MS_parameter_set[j][4] == 2:
                        counter_BS1_channels = counter_BS1_channels -1 #release channel
                        call_completed_sucessfully_BS1 = call_completed_sucessfully_BS1 + 1
                        
                    MS_parameter_set[j][5] = 0 #call status "Down"
                    MS_parameter_set[j][6] = 0 #call duration reset
                    
                else:
                    d_bs0 = distance_BS0(MS_parameter_set[j][0])
                    d_bs1 = distance_BS1(MS_parameter_set[j][0])
                    
                    rsl_BS0 = RSL(frequency_BS0, d_bs0)
                    rsl_BS1 = RSL(frequency_BS1, d_bs1)
                    MS_parameter_set[j][2] = rsl_BS0
                    MS_parameter_set[j][3] = rsl_BS1
                    
                    if MS_parameter_set[j][4] == 1: #for Base Station 1
                        rsl = rsl_BS0
                        rsl2 = rsl_BS1
                        
                        if rsl < RSL_threshold and rsl2 < RSL_threshold:
                            call_block_lack_signal_strength_BS0 = call_block_lack_signal_strength_BS0 + 1
                            counter_BS0_channels = counter_BS0_channels -1
                            MS_parameter_set[j][5] = 0 #call status "Down"
                            MS_parameter_set[j][6] = 0 #call duration reset
                            
                        elif  (rsl < RSL_threshold and rsl2 >= RSL_threshold):  
                            
                            if rsl2 < rsl + margin_handoff:
                                call_block_lack_signal_strength_BS0 = call_block_lack_signal_strength_BS0 + 1
                                counter_BS0_channels = counter_BS0_channels -1
                                MS_parameter_set[j][5] = 0 #call status "Down"
                                MS_parameter_set[j][6] = 0 #call duration "reset"
                                                                
                            elif rsl2 >= rsl+ margin_handoff:
                                
                                call_dropped_lack_signal_strength_BS0 = call_dropped_lack_signal_strength_BS0 + 1
                                counter_BS0_channels = counter_BS0_channels -1
                                MS_parameter_set[j][5] = 0 #call status "Down"
                                MS_parameter_set[j][6] = 0 #call duration reset
                                call_handoff_failures_BS0 = call_handoff_failures_BS0 + 1
                                call_handoff_failures_BS1 = call_handoff_failures_BS1 + 1
                                
                        elif rsl >= RSL_threshold and rsl2 >= rsl + margin_handoff:
                            
                            if counter_BS1_channels < BS1_channels:
                                counter_BS1_channels = counter_BS1_channels + 1 #Channel Allocation
                                counter_BS0_channels = counter_BS0_channels - 1 #Channel Release
                                call_successfull_handoffs_BS0 = call_successfull_handoffs_BS0 + 1
                                call_successfull_handoffs_BS1 = call_successfull_handoffs_BS1 + 1
                                MS_parameter_set[j][4] = 2 #changing Base Station Handover
                                
                            else:
                                call_handoff_failures_BS1 = call_handoff_failures_BS1 + 1
           
                    elif MS_parameter_set[j][4] == 2: #for Base Station 2
                        
                        rsl = rsl_BS1             
                        rsl2 = rsl_BS0
                        
                        if rsl < RSL_threshold and rsl2 < RSL_threshold:
                            call_block_lack_signal_strength_BS1 = call_block_lack_signal_strength_BS1 + 1
                            counter_BS1_channels = counter_BS1_channels - 1
                            MS_parameter_set[j][5] = 0 #call status "Down"
                            MS_parameter_set[j][6] = 0 #call duration reset
                            
                        elif  (rsl < RSL_threshold and rsl2 >= RSL_threshold):
                            
                            if rsl2 < rsl+ margin_handoff:
                                call_block_lack_signal_strength_BS1 = call_block_lack_signal_strength_BS1 + 1
                                counter_BS1_channels = counter_BS1_channels - 1
                                MS_parameter_set[j][5] = 0 #call status "Down"
                                MS_parameter_set[j][6] = 0 #call duration reset
                                
                            elif rsl2 >= rsl+ margin_handoff:
                                call_dropped_lack_signal_strength_BS1 = call_dropped_lack_signal_strength_BS1 + 1
                                counter_BS1_channels = counter_BS1_channels -1
                                MS_parameter_set[j][5] = 0 #call status "Down:
                                MS_parameter_set[j][6] = 0 #call duration reset
                                call_handoff_failures_BS0 = call_handoff_failures_BS0 + 1
                                call_handoff_failures_BS1 = call_handoff_failures_BS1 + 1
                                
                        elif rsl >= RSL_threshold and rsl2 >= rsl + margin_handoff:
                            if counter_BS0_channels < BS0_channels:
                                counter_BS0_channels = counter_BS0_channels + 1 #channel allocation
                                counter_BS1_channels = counter_BS1_channels - 1 #channel release
                                call_successfull_handoffs_BS0 = call_successfull_handoffs_BS0 + 1
                                call_successfull_handoffs_BS1 = call_successfull_handoffs_BS1 + 1
                                MS_parameter_set[j][4] = 1 #changing Base Station Handover
                                
                            else:
                                call_handoff_failures_BS0 = call_handoff_failures_BS0 + 1
                               
        # Mobile Appearance Scenario
        if rnd.random() >= mobile_appearance_rate:
            
            new_mobile_loc = rnd.uniform(0,6)
            new_dir = rnd.randint(0,2)
            
            if new_dir == 0:
                MS_parameter_set[new_mobile_initial_sr_no] = [new_mobile_loc,-0.01,0,0,0,0,0]
            else:
                MS_parameter_set[new_mobile_initial_sr_no] = [new_mobile_loc,0.01,0,0,0,0,0]
            
            new_mobile_initial_sr_no = new_mobile_initial_sr_no + 1
   
    # Calculating Grade of Service
    GOS_BS0 = (call_block_lack_signal_strength_BS0 + call_block_lack_capacity_BS0 + call_dropped_lack_signal_strength_BS0)/call_attempts_BS0
    GOS_BS1 = (call_block_lack_signal_strength_BS1 + call_block_lack_capacity_BS1 + call_dropped_lack_signal_strength_BS1)/call_attempts_BS1
    
    #Handoff Failure Rate
    handoff_failure_rate_BS0 = call_handoff_failures_BS0/(call_handoff_failures_BS0 + call_successfull_handoffs_BS0)
    handoff_failure_rate_BS1 = call_handoff_failures_BS1/(call_handoff_failures_BS1 + call_successfull_handoffs_BS1)
    
    #Traffic Intensity (Erlang)
    traffic_intensity_BS0 = total_time_call_up_BS0 / iteration_time
    traffic_intensity_BS1 = total_time_call_up_BS1 / iteration_time
        
    
    print("call_block_lack_capacity_BS0 = ",call_block_lack_capacity_BS0)
    print("call_block_lack_capacity_BS1 = ", call_block_lack_capacity_BS1)
    print("call_block_lack_signal_strength_BS0 = ",call_block_lack_signal_strength_BS0)
    print("call_block_lack_signal_strength_BS1 = ", call_block_lack_signal_strength_BS1)
    print("call_attempts_BS0 =", call_attempts_BS0)
    print("call_attempts_BS1 =",call_attempts_BS1)
    print("call_successfull_handoffs_BS0 = ", call_successfull_handoffs_BS0)
    print("call_successfull_handoffs_BS1 = ",call_successfull_handoffs_BS1)
    print("Call_handoff_failures_BS0 = ",call_handoff_failures_BS0)
    print("Call_handoff_failures_BS1 = ",call_handoff_failures_BS1)
    print("call_dropped_lack_signal_strength_BS0 = ",call_dropped_lack_signal_strength_BS0)
    print("call_dropped_lack_signal_strength_BS1 = ",call_dropped_lack_signal_strength_BS1)
    print("call_completed_sucessfully_BS0 = ",call_completed_sucessfully_BS0)
    print("call_completed_sucessfully_BS1 = ",call_completed_sucessfully_BS1)
    print("total_time_call_up_BS0 = ",total_time_call_up_BS0)
    print("total_time_call_up_BS1 = ",total_time_call_up_BS1)
    print("GOS_BS0 = ", GOS_BS0)
    print("GOS_BS1 = ", GOS_BS1)
    print("handoff_failure_rate_BS0 = ",handoff_failure_rate_BS0)
    print("handoff_failure_rate_BS1 = ", handoff_failure_rate_BS1)
    print("traffic_intensity_BS0 = ",traffic_intensity_BS0)
    print("traffic_intensity_BS1 = ",traffic_intensity_BS1)
    print("----------------------------------------------------------------------------------------------------------------------------------------------")
   
    return([call_block_lack_capacity_BS0,call_block_lack_capacity_BS1,call_block_lack_signal_strength_BS0, call_block_lack_signal_strength_BS1, call_attempts_BS0, call_attempts_BS1,call_successfull_handoffs_BS0, call_successfull_handoffs_BS1, call_handoff_failures_BS0, call_handoff_failures_BS1, call_dropped_lack_signal_strength_BS0, call_dropped_lack_signal_strength_BS1, call_completed_sucessfully_BS0, call_completed_sucessfully_BS1, total_time_call_up_BS0, total_time_call_up_BS1, GOS_BS0, GOS_BS1, handoff_failure_rate_BS0, handoff_failure_rate_BS1, traffic_intensity_BS0, traffic_intensity_BS1])    
