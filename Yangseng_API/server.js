const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const moment = require('moment');
const { exec } = require('child_process');
const swaggerUi = require('swagger-ui-express');
const swaggerFile = require('./swagger_output.json');
const { log } = require('console');

const app = express();
const port = 3000;

// 將 base64 格式的資料轉換為 Blob 格式（Buffer）
function base64ToBlob(base64Data) {
  const binaryData = Buffer.from(base64Data, 'base64');
  return binaryData;
}

// 將 Blob 格式的資料儲存為圖片檔案
function blobToImage(blobData, outputPath) {
  fs.writeFileSync(outputPath, blobData);
}

app.use(express.json({ limit: '1024mb' }));
app.use(express.urlencoded({ limit: '1024mb', extended: true }));

app.use(cors());
app.use(express.json());

app.post('/api/upload', (req, res) => {
  const { user_name, employee_name, f_image, b_image, l_image, r_image } = req.body;

  const baseUserDir = '../user_images/';

  try {
    if (!fs.existsSync(baseUserDir)) {
      fs.mkdirSync(baseUserDir);
    }

    const userDir = path.join(baseUserDir, user_name);

    if (!fs.existsSync(userDir)) {
      fs.mkdirSync(userDir);
    }

    const currentDate = moment().format('YYYYMMDD');

    const saveImage = (image, pose, outputDir) => {
      const base64Data = image.replace(/^data:image\/\w+;base64,/, '');
      const blobData = base64ToBlob(base64Data);
      const imagePath = path.join(outputDir, `${user_name}_${pose}_${currentDate}.jpg`);
      try {
        blobToImage(blobData, imagePath);
        return imagePath;
      } catch (error) {
        console.error(`儲存圖片時發生錯誤：${error}`);
        throw new Error('儲存圖片失敗');
      }
    };

    const sidePoseDir = path.join(userDir, 'Side_pose/');
    if (!fs.existsSync(sidePoseDir)) {
      fs.mkdirSync(sidePoseDir);
    }

    const sideImagePaths = [
      { image: l_image, pose: 'left' },
      { image: r_image, pose: 'right' },
    ].map(({ image, pose }) => saveImage(image, pose, sidePoseDir));

    const upPoseDir = path.join(userDir, 'Up_pose/');
    if (!fs.existsSync(upPoseDir)) {
      fs.mkdirSync(upPoseDir);
    }
    const Dir = path.join(userDir, 'Oringin/');
    if (!fs.existsSync(Dir)) {
      fs.mkdirSync(Dir);
    }

    const upImagePaths = [
      { image: f_image, pose: 'front' },
      { image: b_image, pose: 'back' },
    ].map(({ image, pose }) => saveImage(image, pose, upPoseDir));
    //原始照片儲存
    const upImagePaths2 = [
      { image: f_image, pose: 'front' },
      { image: b_image, pose: 'back' },
    ].map(({ image, pose }) => saveImage(image, pose, Dir));
    const upImagePaths3 = [
      { image: l_image, pose: 'left' },
      { image: r_image, pose: 'right' },
    ].map(({ image, pose }) => saveImage(image, pose, Dir));


    exec(`python main.py ${employee_name} ${user_name} ${sidePoseDir} ${upPoseDir}`, (error, stdout, stderr) => {
      if (error) {
        console.error(`執行 main.py 時發生錯誤：${error}`);
         // 如果發生錯誤，執行 clear.py
        exec(`python Clear.py ${user_name}`, (clearError, clearStdout, clearStderr) => {
          if (clearError) {
            console.error(`執行 clear.py 時發生錯誤：${clearError}`);
          } else {
            console.log(clearStdout);
            console.log('成功執行 clear.py');
          }
        });
  
        res.status(502).json({
          error: '缺少正確圖片，無法執行 main.py',
        });
        return;
      } else {
        res.status(200).json({
          message: '圖像儲存成功並執行 main.py',
        });
      }
    });
  } catch (error) {
    console.error(`處理上傳圖片時發生錯誤：${error}`);
    res.status(500).json({ error: '伺服器錯誤' });
  }
});

// 新增一個 /api/getUserImages GET 請求的處理函式
app.get('/api/getUserImages/:user_name', (req, res) => {
  const user_name = req.params.user_name;

  try {
    // 使用者資料夾路徑
    const userDir = path.join('../user_images/', user_name);

    // 確保使用者資料夾存在
    if (!fs.existsSync(userDir)) {
      res.status(404).json({ error: '找不到使用者資料夾' });
      return;
    }

    // 讀取使用者資料夾內的所有圖片檔案
    const imageFiles = fs.readdirSync(userDir).filter(file => file.endsWith('.png') || file.endsWith('.jpg'));

    // 建立一個陣列，包含每個圖片檔案的時間戳
    const userRelatedDatetime = imageFiles.map(file => {
      // 提取年月日時分
      const fileTimestamp = file.match(/\d{8}_\d{6}/);
      if (fileTimestamp) {
        const [year, month, day, hour, minute] = [
          fileTimestamp[0].substring(0, 4),
          fileTimestamp[0].substring(4, 6),
          fileTimestamp[0].substring(6, 8),
          fileTimestamp[0].substring(9, 11),
          fileTimestamp[0].substring(11, 13)
        ];
        return `${year}${month}${day}_${hour}${minute}`;
      } else {
        // 若檔案名稱中找不到時間戳，直接使用原檔案名稱
        return file;
      }
    });

    res.status(200).json({
      message: '成功取得使用者圖片列表',
      userRelatedDatetime: userRelatedDatetime,
    });
  } catch (error) {
    console.error(`取得使用者圖片列表時發生錯誤：${error}`);
    res.status(500).json({ error: '伺服器錯誤' });
  }
});

app.get('/api/getText/:user_name', (req, res) => {
  const user_name = req.params.user_name;
  const { datetime } = req.query;
  try {
    const userDir = path.join('../user_images/', user_name);
    if (!fs.existsSync(userDir)) {
      res.status(404).json({ error: '找不到使用者資料夾' });
      return;
    }
    // read data.txt
    const dataPath = path.join(userDir, 'data.txt');
    if (!fs.existsSync(dataPath)) {
      res.status(404).json({ error: '找不到使用者資料夾' });
      return;
    }
    function suggest(dataangle){
      if(Math.abs(dataangle)>=10.0){
        return "建議就醫";
      }
      else if(Math.abs(dataangle)>=5.0){
        return "前往復健";
      }
      else{
        return "繼續保持";
      }
    }
    const data = fs.readFileSync(dataPath, 'utf8');
    const dataangle = 90.0-parseFloat(data.split(' ')[0]);
    const result = Math.abs(90.0-parseFloat(data.split(' ')[0]))>=10.0?"脊椎彎曲":"健康";
    // 讓我的suggest 分成三類 1.繼續保持 2.建議就醫 3.前往復健
    const suggests = suggest(dataangle);

    const combinedata = {
      data: data,
      dataangle: dataangle,
      result: result,
      suggest: suggests
    }
    res.status(200).json({
      message: '成功取得使用者資料',
      data: combinedata,
    });
  } catch (error) {
    console.error(`取得使用者資料時發生錯誤：${error}`);
    res.status(500).json({ error: '伺服器錯誤' });
  }
});


// 我要要一個url 可以取得圖片

// 設置靜態文件夾
app.use(express.static(path.join(__dirname, '../user_images/')));



// 處理取得圖片的請求
app.get('/api/get-image/:id', (req, res) => {
    const imageid = req.params.id; // 假設圖片名稱是動態的

    // find the floder only png 
    const userDir = path.join('../user_images/', imageid);
    const imageFiles = fs.readdirSync(userDir).filter(file => file.endsWith('.png'));
    const imageName = imageid+'/'+imageFiles; // 假設圖片名稱是固定的
    
    const imagePath = path.join(__dirname, '../user_images', imageName);

    // 返回圖片
    res.sendFile(imagePath);
});




app.get('/api/getDateImages/:user_name', (req, res) => {
  const user_name = req.params.user_name;
  const { datetime } = req.query;

  try {
    const userDir = path.join('../user_images/', user_name);

    if (!fs.existsSync(userDir)) {
      res.status(404).json({ error: '找不到使用者資料夾' });
      return;
    }

    const imageFiles = fs.readdirSync(userDir).filter(file => {
      return file.includes(datetime);
    });

    if (imageFiles.length === 0) {
      res.status(404).json({ error: '找不到對應的圖片' });
      return;
    }

    const firstImageFile = imageFiles[0];
    const filePath = path.join(userDir, firstImageFile);
    const fileData = fs.readFileSync(filePath);
    
    // 將圖片的base64資料轉換成Buffer
    const imageBuffer = Buffer.from(fileData);

    // 返回Buffer數據到前端
    res.status(200).json({
      message: '成功取得使用者指定日期時間的圖片',
      userImage: imageBuffer.toString('base64'), // 在前端再轉換回base64顯示圖片
    });
  } catch (error) {
    console.error(`取得使用者指定日期時間的圖片時發生錯誤：${error}`);
    res.status(500).json({ error: '伺服器錯誤' });
  }
});

// show photo by url 


app.post('/api/upimage', async (req, res) => {
  const { user_name, employee_name, f_image, b_image, l_image, r_image } = req.body;
  const baseUserDir = '../user_images/';
  const currentDate = moment().format('YYYYMMDD');

  try {
    if (!fs.existsSync(baseUserDir)) {
      fs.mkdirSync(baseUserDir);
    }

    const userDir = path.join(baseUserDir, user_name);

    if (!fs.existsSync(userDir)) {
      fs.mkdirSync(userDir);
    }

    const sidePoseDir = path.join(userDir, 'Side_pose/');
    if (!fs.existsSync(sidePoseDir)) {
      fs.mkdirSync(sidePoseDir);
    }

    const upPoseDir = path.join(userDir, 'Up_pose/');
    if (!fs.existsSync(upPoseDir)) {
      fs.mkdirSync(upPoseDir);
    }

    const saveImageFromBuffer = async (imageBuffer, pose, outputDir) => {
      const imagePath = path.join(outputDir, `${user_name}_${pose}_${currentDate}.jpg`);
      try {
        await fs.promises.writeFile(imagePath, imageBuffer);
        return imagePath;
      } catch (error) {
        console.error(`儲存圖片時發生錯誤：${error}`);
        throw new Error('儲存圖片失敗');
      }
    };

    const saveImagesPromises = [];

    const sideImagePromises = [
      { image: l_image, pose: 'left' },
      { image: r_image, pose: 'right' },
    ].map(({ image, pose }) => saveImageFromBuffer(Buffer.from(image, 'base64'), pose, sidePoseDir));

    const upImagePromises = [
      { image: f_image, pose: 'front' },
      { image: b_image, pose: 'back' },
    ].map(({ image, pose }) => saveImageFromBuffer(Buffer.from(image, 'base64'), pose, upPoseDir));

    saveImagesPromises.push(...sideImagePromises);
    saveImagesPromises.push(...upImagePromises);

    // 等待所有图片保存完成
    await Promise.all(saveImagesPromises);

    // 响应前端，告知图片保存成功
    res.status(200).json({
      message: '圖像儲存成功',
    });

    // 執行影像辨識
    execImageRecognition(employee_name, user_name, sidePoseDir, upPoseDir);
  } catch (error) {
    console.error(`處理上傳圖片時發生錯誤：${error}`);
    res.status(500).json({ error: '伺服器錯誤' });
  }
});



function execImageRecognition(employee_name, user_name, sidePoseDir, upPoseDir) {
  exec(`python main.py ${employee_name} ${user_name} ${sidePoseDir} ${upPoseDir}`, (error, stdout, stderr) => {
    if (error) {
      console.error(`執行 main.py 時發生錯誤：${error}`);
      // 如果發生錯誤，執行 clear.py
      exec(`python Clear.py ${user_name}`, (clearError, clearStdout, clearStderr) => {
        if (clearError) {
          console.error(`執行 clear.py 時發生錯誤：${clearError}`);
        } else {
          console.log(clearStdout);
          console.log('成功執行 clear.py');
        }
      });
    } else {
      console.log(stdout);
      console.log('成功執行 main.py');
    }
  });
}



app.use('/api-doc', swaggerUi.serve, swaggerUi.setup(swaggerFile));
app.listen(port, () => {
  console.log(`伺服器正在監聽埠號 ${port}`);
});
