def autoencoder(relative_time, absolute_time, amplitude):
    model = torch.load('app/processing/encoder.pth')
    model.eval()

    ds = xr.Dataset(
        {
            'wave': (['relative_time'], amplitude)
        },
        coords={
            'relative_time': (['relative_time'], relative_time), 
        }
    )

    ds.to_netcdf('output_data.nc')

    print("CSV data successfully converted to NetCDF format!")

    file_path = 'output_data.nc'
    data = xr.open_dataset(file_path)

    # Reshape the input data
    input_data = data['wave'].values
    input_data = input_data.reshape(-1, input_data.shape[-1])
    input_data = torch.tensor(input_data).float()

    # Process each channel separately
    outputs = []
    with torch.no_grad():
        for channel in input_data:
            channel_input = channel.unsqueeze(0) 
            channel_output = model(channel_input)
            outputs.append(channel_output.squeeze().numpy())
            
    print('Done infering...')

    output_data = np.array(outputs).T

    min_length = min(len(relative_time), len(output_data))
    absolute_time = absolute_time[:min_length]
    relative_time = relative_time[:min_length]
    print("relative_time", relative_time.shape)
    output_data = output_data[:min_length, 0]
    print("output_data", output_data.shape)

    combined_df = pd.DataFrame({
        'time_abs(%Y-%m-%dT%H:%M:%S.%f)': absolute_time,
        'time_rel(sec)': relative_time,
        'velocity(m/s)': output_data.flatten()  
    })

    return combined_df