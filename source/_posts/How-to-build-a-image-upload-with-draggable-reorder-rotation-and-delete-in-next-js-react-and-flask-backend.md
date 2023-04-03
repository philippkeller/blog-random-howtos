---
title: >-
  How to build image upload with draggable reorder, rotation and delete in
  next.js/react and python backend
date: 2023-03-12 16:11:15
tags:
scripts:
- http://cdn.jsdelivr.net/npm/highlightjs-line-numbers.js@2.8.0/dist/highlightjs-line-numbers.min.js
- /files/linenumbers.js
css:
- "pre .hljs-ln-code {padding-left: 10px}"
- "table.hljs-ln tr td {border: none}"
- "table.hljs-ln > tbody > tr:nth-child(odd) > td {background: none}"
- "td.hljs-ln-line.hljs-ln-numbers { color: #ccc !important }"
- "div.post-content > pre > code > table { margin-bottom: 0 }"

---
<img class="caption" alt="What we'll be building today" src="/images/upload.gif"  />

This howto covers:

- image upload with `<input type="file" multiple />` component
- frontend in next.js (97% is react, so if you're using react this howto should work for you too)
- backend in python: uploading to s3 (I'm using Flask but 97% is framework agnostic)
- image reordering with [dndkit](https://dndkit.com/)
- image deletion
- image rotation in python using Pillow

<!-- more -->

<div style="clear: both; margin-bottom: 5em" />

## Uploading images

There's a popular library called [Dropzone](https://www.dropzone.dev/) which offers a [react library](https://react-dropzone.js.org/) but I never really saw the point of a "drag and drop landing zone". I'm an old fashioned "click this button to upload" guy.

The following code shows a button, when the button is clicked it opens the file dialogue which lets the user choose **multiple files** but only those of type image:

<div style="clear: both" />


```javascript
import { PhotoIcon } from "@heroicons/react/20/solid";
import { useRef } from "react";

export default function Example() {
    const inputFileRef = useRef();
    return (
            <div className='m-5'>
                <input id="file_upload" type="file" multiple
                    accept="image/*" className='hidden' 
                    ref={inputFileRef}
                    onChange={onImageUpload} 
                    />
                <button
                    type="button"
                    onClick={() => inputFileRef.current.click()}
                    className="inline-flex items-center gap-x-2 rounded-md
                    bg-indigo-600 py-2 px-3 text-sm font-semibold text-white">
                    <PhotoIcon className="-ml-0.5 h-5 w-5" aria-hidden="true" />
                    Upload images
                </button>
            </div>

    )
}
```

I'm using tailwindCSS and the `PhotoIcon` is from heroicons (`npm i @heroicons/react`), but of course you can adapt this to your liking.

Next is of course to add the code for uploading the images. On javascript side that's what I use:

```javascript
const [isUploading, setIsUploading] = useState(false)
const [images, setImages] = useState([])
const onImageUpload = async (e) => {
    const files = e.target.files;
    const data = new FormData()
    for (var i = 0; i < files.length; i++) {
        data.append(`file-${i}`, files[i], files[i].name);
    }
    setIsUploading(true)
    const res = await fetchJson('/api/upload', {
        method: 'POST',
        body: data,
    })
    setImages(images.concat(res.filenames))
    setIsUploading(false)
}
```

Some explanations:

- Line 1,9,15: I want to let the user know a file is uploading -> I'm using `isUploading` for this
- Line 6: granted, that's an ugly way to loop over the images. You might know a nicer way, but this was good enough for me
- Line 10: `fetchJson` is a helper function I use which adds servername, error handling etc. I'm leaving this out as I'm assuming you have a similar function already
- Line 14: the backend will return an array of filenames with paths which I'm saving in the `images` variable

This is all very much straight forward! So really no need to use any libraries for this. Let's have a look at the backend code. I'm using flask but the code is pretty much the same in any framework:

```python
from flask import request, jsonify
import boto3
import shortuuid

id_generator = shortuuid.ShortUUID()

@app.route('/api/upload', methods=['POST'])
def upload():
    files = list(request.files.items())
    s3 = boto3.client('s3')
    bucket = 'my-s3-bucket'
    path = f'upload'
    paths = []
    for _,file in files:
        ending = file.filename.split('.')[-1]
        if ending in ['jpg', 'jpeg']:
            content_type = 'image/jpeg'
        else:
            content_type = f'image/{ending}'
        fileid = id_generator.random(length=10)
        filename = f'{path}/{fileid}.{ending}'
        s3.upload_fileobj(file.stream, bucket, filename, 
                          ExtraArgs={"ContentType": content_type})
        paths.append(filename)
    return jsonify(dict(filenames=paths))
```

Again, some explanations:

- Line 20: in order to have no filename clashes on s3, I'm generating a random 10 length string, containing upper+lowercase letters and numbers. That's 10^17 possible strings, pretty safe I'd say. You'd need to `pip install shortuuid` to use this
- Line 16-19: In order that the browsers correctly show the images from s3, you need to specify the mime type on upload. I guess there are better ways to do this, but this code has done the trick for me so far
- Line 22: note that the file is uploaded from memory, no messing around with temporary files

If you care for speed, you'd want to run this with multi-threading or multi-processing, but for my case it seemed fast enough.

What's missing on the client side is the loading animation: After `Upload images` paste this code:

```javascript
Upload images
{isUploading && (
  <LoadingAnimation className="fill-white w-6 h-6" />
)}
```

If you want to use my `LoadingAnimation` then copy-paste [this code](https://gist.github.com/philippkeller/1e561c95eb48111d4b4abd5dcf553737) into a separate module.

## Show images and make them draggable

I used **hours** to find a good library which supports drag and drop for react. Every library was either no longer supported (react-beautiful-dnd) or looked complicated to use (react-dnd), I ended up using [dnd kit](https://dndkit.com/), the »new kit on the block«. It doesn't yet show up on the first page of google search, but has already 7.2K stars on github at the time of this blogpost (March 2023).

I was unsure if mobile was supported, as their doc is not clear about this part (and their example on their homepage does **not** work with mobile), but rest assured, the code covered in this howto works on mobile too!

To install it:

```
npm install @dnd-kit/core  @dnd-kit/sortable
```

The following example is mainly taken from [the official documentation](https://docs.dndkit.com/presets/sortable/sortable-context).

First, you'd need these additional imports:

```python
import { closestCenter, DndContext, KeyboardSensor, PointerSensor, useSensor, useSensors } from "@dnd-kit/core";
import { arrayMove, SortableContext, sortableKeyboardCoordinates } from "@dnd-kit/sortable";
import Image from "next/image";
```

If you're using react, you can omit the `Image` import and you can just `<img>` later.

Then, you'd need those two additional functions

```javascript
const sensors = useSensors(
    useSensor(PointerSensor, {
        activationConstraint: {
            distance: 8,
        },
    }),
    useSensor(KeyboardSensor, {
        coordinateGetter: sortableKeyboardCoordinates,
    })
);
const handleDragEnd = (event) => {
    const { active, over } = event;

    if (active.id !== over.id) {
        setImages((images) => {
            const oldIndex = images.indexOf(active.id);
            const newIndex = images.indexOf(over.id);

            return arrayMove(images, oldIndex, newIndex);
        });
    }
}
```

### Sensors

`sensors` defines with what you can move the images:

- a **pointer sensor** is needed for moving the images with a mouse (on desktop) or touch (on mobile). I added `activationContraint` to be able to click on elements (delete, rotate) later without the drag operation to start already
- a **keyboard sensor** lets you move the items using tab, space, left/right control. Not super intuitive, but fancy nonetheless

### handleDragEnd

The `handleDragEnd` performs the switch on the images array. So the move is actually reflected on the array which you can store in a database later to store the order.

<p style="margin-top: 5em; margin-bottom: 5em;"></p>

Finally the html part. Put this above the `<input>` element:

```
<DndContext sensors={sensors} collisionDetection={closestCenter}
            onDragEnd={handleDragEnd}>
    <SortableContext items={images}>
        <ul role="list" className="grid grid-cols-4 gap-x-4 gap-y-8">
            {images.map((file) => (
                <li key={file}>
                    <SortableItem id={file}>
                        <div className="group w-full overflow-hidden
                                        rounded-lg bg-gray-100">
                            <div className="aspect-4/3 overflow-hidden relative">
                                <Image priority fill 
                                       src={`https://example.com/${file}`}
                                       sizes="22vw" alt="" 
                                       className="object-scale-down />
                            </div>
                        </div>
                    </SortableItem>
                </li>
            ))}
        </ul>

    </SortableContext>
</DndContext>
```

You see the code is quite straight forward, that's what I like about dndkit. The only extra thing you need is top copy-paste [`SortableItem`](https://gist.github.com/philippkeller/05061029645dd7be9da6fa0e4c9d1b1c) into an own component and import this. This is mostly taken from [here](https://docs.dndkit.com/presets/sortable/usesortable) with the only addition that I added `props.children`.

Some explanations about the code:

- Line 1: `collisionDetection` defines when images should move by the side. If you want to play with this, [see the docs](https://docs.dndkit.com/api-documentation/context-provider/collision-detection-algorithms)
- Line 10: I created a 4/3 aspect via tailwindcss config (see [doc](https://tailwindcss.com/docs/aspect-ratio#customizing-your-theme))
- Line 12: I'm serving the image from s3 through cloudfront. This is needed for SSL. If you don't need SSL, you can serve them directly from S3 once you make the bucket world-readable.
- Line 11-14: Instead of the Image component, img works as well, I had some problems with showing portrait mode images properly (without having them filling the whole canvas). Only `<Image>` solved this issue for me. If you're a skilled CSS/React person, you can solve this with some additional styling I'm sure.

That's it already for ordering the images! Congrats on reaching this far. If you don't need deletion and rotation then you can stop at this point!

## Deletion

Delete is quite simple and I was lazy and only implemented the client side 😅

After the closing div after `<Image>`, add this code:


```javascript
<div className="m-2 flex justify-center truncate text-sm font-medium text-gray-900">
    <!-- rotation icons -->
    <TrashIcon className='h-4 z-20' onClick={handleDelete} img-id={file} />
</div>
```

The `TrashIcon` is taken from heroicons (`npm i @heroicons/react`).

The deletion handler:

```
const handleDelete = (e) => {
        const path = e.currentTarget.getAttribute('img-id')
        setImages(images.filter(item => item !== path))
}
```

That's it 😇. Super sneaky lazy, but I don't bother doing the deletion on s3. I'll handle this separately as I'll need to handle aborted form submissions anyway and will run a daily "delete orphaned images" job on the backend.

## Rotation

This is somehow a nice-to-have feature, because you could argue that users can do this on their laptop. Thing is, many have no idea how to do this and handling image rotation in python is fun, so…

First, add the rotate-left and rotate-right icons, I used inline svg for this. This is ugly but straightforward. And by now you probably guess how I roll: If it works, it works 😎.

Copy-paste [this gist](https://gist.github.com/philippkeller/0705772f92fbae585ae1bc0dee773b26) where the `<!-- rotation icons -->` is in the code above. This has a click handler into `handleRotateLeft` and `handleRotateRight`. Here's the code for both functions:

```javascript
const handleRotate = async (path, direction) => {
    setIsRotationLoading(path)
    const res = await fetchJson(`/api/rotate/${direction}`, {
        method: 'POST',
        body: JSON.stringify({ path: path }),
        headers: {
            'Content-Type': 'application/json'
        },
    })
    const images_new = images.map(u => u == path ? res.filename : u);
    setImages(images_new)
    setIsRotationLoading('')
}

const handleRotateRight = (e) => {
    const path = e.currentTarget.getAttribute('img-id')
    handleRotate(path, 'right')
}
const handleRotateLeft = (e) => {
    const path = e.currentTarget.getAttribute('img-id')
    handleRotate(path, 'left')
}
```

Again some explanations:

- Line 1: `direction` is a string, either `left` or `right`, an enum would have been cleaner but let's stay brief here
- Line 2,12: as the image rotation takes about half a second, I'm showing a little loading animation under the image which is rotating. I'm leaving the html part as an exercise for the reader 👨‍🏫.
- Line 7: If you omit sending the content-type, it will cause [strange exceptions in the python backend](https://stackoverflow.com/a/20001283/119861)
- Line 10: The backend will rotate the image and will respond with a new image path. It was easier to change the path, as this way I'm sure the client fetches the image afresh. Replacing the image without changing the path/filename would create lots of caching issues which was not worth to deal with.

And finally the backend code in python.

You'd need to `pip install Pillow` which we need to rotate the image.

```python

from flask import request
import boto3
from io import BytesIO
from PIL import Image

def _rotate(orig, rotation):
    s3 = boto3.client('s3')
    s3_response_object = s3.get_object(Bucket='my-s3-bucket', Key=orig)
    object_content = s3_response_object['Body'].read()
    b = BytesIO(object_content)
    img = Image.open(b)
    img2 = img.transpose(rotation)
    output = BytesIO()
    img2.save(output, format=img.format)
    output.seek(0)
    ending = orig.split('.')[-1]
    if ending in ['jpg', 'jpeg']:
        content_type = 'image/jpeg'
    else:
        content_type = f'image/{ending}'
    fileid = id_generator.random(length=10)
    path = f'upload'
    filename = f'{path}/{fileid}.{ending}'
    s3.upload_fileobj(output, 'my-s3-bucket', filename, 
                      ExtraArgs={"ContentType": content_type})

    return jsonify(dict(filename=filename))


@app.route('/api/rotate/right', methods=['POST'])
def rotate_right():
    data = request.get_json()
    orig = data['path']
    return _rotate(orig, Image.ROTATE_90)

@app.route('/api/rotate/left', methods=['POST'])
def rotate_left():
    data = request.get_json()
    orig = data['path']
    return _rotate(orig, Image.ROTATE_270)

```

Again, some explanations:

- Lines 9-12: `BytesIO` and `get_object` avoids messing around with temp files. Temp files are always a hassle as they produce clutter and need to be removed and stuff
- Lines 13-16: the rotation also happens in memory. `seek(0)` is needed to put the file pointer to the beginning of the file, otherwise `upload_fileobj` will upload an empty file.
- Lines 17-26: see the notes on the backend code for uploading further up of this howto

And that's it. I hope I didn't forget anything! If I did, as always: leave a comment, I hope to follow up quickly.