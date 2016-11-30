var collection_index = {
    'term': ['学期代码'],
    'major': ['专业代码'],
    'course': ['课程代码'],
    'student': ['学号'],
    'plan': ['学期代码', '课程代码', '课程代码'],
    'class': ['学期代码', '课程代码', '教学班号'],
    'class_student': ['学期代码', '课程代码', '教学班号', '学号']
};

function dropDuplicate(collection, keys) {
    // http://stackoverflow.com/questions/14184099/fastest-way-to-remove-duplicate-documents-in-mongodb
    // https://docs.mongodb.com/manual/aggregation/
    var id = {};
    var duplicates = [];
    for (var idx in keys) {
        var key = keys[idx];
        id[key] = '$' + key;
    }
    db[collection].aggregate([
            // {
            //     $match: {
            //         // name: {"$ne": ''}  // discard selection criteria
            //     }
            // },
            {
                $group: {
                    _id: id, // can be grouped on multiple properties

                    dups: {"$addToSet": "$_id"},
                    count: {"$sum": 1}
                }
            },
            {
                $match: {
                    count: {"$gt": 1}    // Duplicates considered as count greater than one
                }
            }
        ],
        {allowDiskUse: true}       // For faster processing if set is larger
    ).forEach(function (doc) {
        // You can display result until this and check duplicates
        doc.dups.shift();      // First element skipped for devaring
        doc.dups.forEach(function (dupId) {
                duplicates.push(dupId);   // Getting all duplicate ids
            }
        )
    });

    // If you want to Check all "_id" which you are devaring else print statement not needed
    printjson(duplicates);
    print(duplicates.length);
    // Remove all duplicates in one go
    db[collection].remove({_id: {$in: duplicates}})

}


for (var k in collection_index) {
    print(k);
    dropDuplicate(k, collection_index[k]);
}
