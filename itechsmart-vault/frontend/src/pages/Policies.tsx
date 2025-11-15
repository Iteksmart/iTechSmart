import { Shield } from 'lucide-react';

const Policies = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-800">Access Policies</h1>
        <p className="text-gray-600 mt-1">Manage access control policies</p>
      </div>
      <div className="card text-center py-12">
        <Shield size={48} className="mx-auto text-gray-400 mb-4" />
        <p className="text-gray-600 text-lg">No policies configured</p>
        <p className="text-gray-500 mt-2">Create policies to control access to secrets</p>
        <button className="btn-primary mt-4">Create Policy</button>
      </div>
    </div>
  );
};

export default Policies;
