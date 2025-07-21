const Admin = require('../models/admin'); // Mongoose model

const addAdminIfNotFound = async () => {
  const admin = await Admin.findOne({ username: 'sysadmin' });
  if (!admin) {
    await Admin.create({
      username: 'sysadmin',
      password: 'systemadmin' // In real apps, hash this!
    });
    console.log('Default admin created');
  }
};

module.exports = addAdminIfNotFound;
