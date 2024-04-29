export const DeviceStatusConstant = {
  DeviceRegistered: "Device Registered",
  DeviceVerified: "Device Verified",
  PaymentProcessed: "Payment Processed",
  DataRetrieved: "Data Retrieved",
  LinkReceived: "Link Received",
};

enum DeviceStatusIndex {
  DeviceRegistered,
  DeviceVerified,
  PaymentProcessed,
  DataRetrieved,
  LinkReceived,
}

interface DeviceStatusComponentProps {
  deviceStatus: string;
  isDeviceRareOrCurrent: boolean;
}

const DeviceStatusComponent: React.FC<DeviceStatusComponentProps> = ({
  deviceStatus,
  isDeviceRareOrCurrent,
}) => {
  const deviceStatusIndex =
    Object.values(DeviceStatusConstant).indexOf(deviceStatus);
  return (
    <html data-theme="lofi" className="bg-transparent">
      <ul className="steps mt-4 bg-transparent w-full">
        {!isDeviceRareOrCurrent
          ? Object.values(DeviceStatusConstant).map((status, index) => (
              <li
                key={status}
                className={`step ${
                  deviceStatusIndex >= index ? "step-primary" : ""
                }`}
              >
                {status}
              </li>
            ))
          : Object.values(DeviceStatusConstant)
              .slice(0, 2)
              .map((status, index) => (
                <li
                  key={status}
                  className={`step ${
                    deviceStatusIndex >= index ? "step-primary" : ""
                  }`}
                >
                  {status}
                </li>
              ))}
      </ul>
    </html>
  );
};

export default DeviceStatusComponent;
