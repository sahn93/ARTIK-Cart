var noble = require('noble');

console.log('mac addr, rssi')

noble.on('stateChange', function(state) {
    if (state === 'poweredOn') {
        noble.startScanning([], true);
    } else {
        noble.stopScanning();
    }
});

noble.on('discover', function(peripheral) {
    console.log(peripheral.address + ',' + peripheral.rssi)
});
