import { ImageIcon, MicIcon, SendIcon } from 'lucide-react';
import { Button } from './ui/button';
import { useState } from 'react';
import { error } from 'console';

const [isRecording, setIsRecording] = useState(false);

async function handleRecording(){
    const options = { mimeType: "video/webm"}
    const stream = await navigator
    .mediaDevices
    .getUserMedia({audio : true})
    .then((audioStream) => {
        const mediaRecorder = new MediaRecorder(audioStream);
        mediaRecorder.addEventListener('click', function (){
            try{
                mediaRecorder.start();
                setIsRecording(true);
                console.log('recording started!')
            }catch(e){
                console.log(e);
            }
        })
    }).catch((error) => {
        console.error(`Error when capturing user audio ${error}`);
        });
}

function AudioButton() {
    return (
        <Button type="button" variant="outline" onClick={() => handleRecording()}>
            <MicIcon className="w-4 h-4" />
        </Button>
    )
}