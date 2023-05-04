%% Monitoring for proper closure of the port
try
    fclose(u)
    delete(u)
    clearvars u
    fprintf('Port was not closed last time\n')
catch
    fprintf('Port was sucessfully closed last time\n')
end
%% Cleanup
clc
close ('all')
clearvars

%% Poviding details for the server cretion
local_ip = '127.0.0.1';                                                     % Local PC IP address
local_port = 9091;                                                          % Port to receive command from python
remote_ip = '127.0.0.1';                                                    % Remote PC IP address
remote_port = 9090;                                                         % Port to send the address at the remote PC

%% Setting up a server nd opening it for future use
u = udp(remote_ip,remote_port,'LocalPort',local_port);                      % creating UDP server
u.OutputBufferSize = 1024;                                                  % providing buffer size to look for
fopen(u)                                                                    % opening port for data sharing
u.timeout = 5;                                                             % setting timeout for executing while loop properly
%% Opening Simulink model during continuous receipt from python command
% % opning the first vehicle model
open_system('ve_model1')
simulator_1 = sdo.SimulationTest('ve_model1');
simulator_1 = fastRestart(simulator_1,'on');

% opening the second vehicle model
open_system('ve_model2')                                                    % opening the model for execution
simulator_2 = sdo.SimulationTest('ve_model2');
simulator_2 = fastRestart(simulator_2,'on');

initial_handshake = false
loop_tracker = 0

%% Confirming the initial handshake for the model
while (initial_handshake == false)
    fwrite(u,'Matlab is ready to receive the data')
    temp = str2double(fscanf(u));
    if temp == 1
        intial_setup = true;
        break
    end
    loop_tracker = loop_tracker+1;
    if loop_tracker > 5
        break
    end
end

%% Setting the initial status for the model 
loop_tracker = 0;
command_pending_checker = 0;
while intial_setup == true
    fwrite(u,'Model to select is');
    temp = str2double(fscanf(u));
    model_to_use = model_selected(temp);
    fwrite(u,model_to_use)
    model_set = true
   % Receiving the model details for setting up the required models
    while (model_set == true)
        fwrite(u,"Send model parameters");
        IntegrationStep = str2double(fscanf(u));
        fwrite(u,"IntegrationStep info received");
        veh_mass = str2double(fscanf(u));
        fwrite(u,"Vehicle mass info received");
        veh_x_0 = str2double(fscanf(u));
        fwrite(u,"Vehicle X0 info received");
        veh_y_0 = str2double(fscanf(u));
        fwrite(u,"Vehicle Y0 info received");
        data_transfer_check = str2double(fscanf(u));
        if data_transfer_check == 1
           model_set = false;
           status = initial_position_set(model_to_use,IntegrationStep,veh_mass,veh_x_0,veh_y_0)
           fwrite(u,status)
        else
            continue
        end
    end
    status = initial_position_set(model_to_use,0.1,1000,0,0)
    command_pending_checker = str2double(fscanf(u));
    if command_pending_checker == -1
        intial_setup = false;
    else
        intial_setup = true;
        loop_tracker = 0;
    end
    loop_tracker = loop_tracker +1;
    if loop_tracker > 5
        break
    end
end

%% Fast start switching
% Required as model can not be closed with fast start on
simulator_1 = fastRestart(simulator_1,'off');
simulator_2 = fastRestart(simulator_2,'off');
%% closing up the server to avoid any error
fclose(u)
delete(u)
clearvars u

%% funtion to identify the model selected
function [mdl_name,model_data_receive] = model_selected(mdl_number)
    if mdl_number == 1
        mdl_name = 've_model1';
        model_data_receive = true;
    elseif mdl_number == 2
        mdl_name = 've_model2'
        model_data_receive = true;
    elseif mdl_number == 3
        mdl_name = 've_model3'
        model_data_receive = true;
    elseif mdl_number == 4
        mdl_name = 've_model4'
        model_data_receive = true;
    end
end

%% function details to set the initial coordinates of the 
function [status] = initial_position_set(mdl,IntegrationStep,mass,X_0,Y_0)
    Simulink.sdi.clear
    % mdl = 've_model2';
    % open_system(mdl)
    simMode = get_param(mdl,'ModelWorkspace');                              % Getting the parameter workspace from simulink
    check = getActiveConfigSet(mdl);                                        % Getting the requied parameter for further setup
    assignin(simMode, 'IntegrationStep',IntegrationStep);                   % Integration step size
    assignin(simMode, 'm',mass);                                            % mass of the vehicle
    assignin(simMode, 'X0',X_0);                                            % initial x0 position of vehicle
    assignin(simMode, 'Y0',Y_0);                                            % intial y0 position of vehicle 
    status = 'Updated';
end