import EWasteHubImage from "../../assets/EWasteHub.jpg";

const LoginPage = () => {
  return (
    <div
      className="min-h-screen flex flex-col"
      style={{ backgroundColor: "hsl(169, 52%, 80%)" }}
    >
      <div className="flex-grow flex justify-center items-center">
        <div className="max-w-4xl w-full bg-white rounded-lg shadow-xl overflow-hidden flex lg:flex-row flex-col-reverse animate-fade-in">
          {/* Image Section */}
          <div className="lg:w-1/2 flex justify-center items-center my-6">
            <div
              className="h-96 w-full bg-cover bg-no-repeat bg-center"
              style={{
                backgroundImage: `url(${EWasteHubImage})`,
                backgroundSize: "contain",
                backgroundPosition: "center",
              }}
            ></div>
          </div>
          {/* Form Section */}
          <div className="lg:w-1/2 p-8 sm:p-12">
            <h2 className="text-3xl font-bold text-gray-800 mb-8 text-center">
              Log In to Your Account
            </h2>
            <form className="space-y-6">
              <input
                type="email"
                placeholder="Email"
                className="input input-bordered w-full bg-gray-50"
              />
              <input
                type="password"
                placeholder="Password"
                className="input input-bordered w-full bg-gray-50"
              />
              {/* Create Account Hyperlink */}
              <div className="text-right mb-6">
                <a href="/register" className="text-sm text-primary link">
                  Don't have an account? Register here
                </a>
              </div>
              {/* Action Buttons */}

              <div className="flex flex-col">
                <button className="btn btn-primary flex">Log In</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
