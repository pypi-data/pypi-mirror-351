# This is a standard code of a GPT (Generative Pre-trained Transformer) model, developed by Sapiens Technology®️,
# which faithfully follows the mathematical structure of the article “Attention Is All You Need” for the construction of the Transformer architecture
# used in the pattern recognition of the model that is saved. Some optimizations that do not influence the Transformer architecture
# were applied only to facilitate the adjustments of the parameters and variables of the training, saving, loading, fine-tuning and inference of the pre-trained model.
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
class GPTModel:
    def __init__(self, embedding_dim=384, block_size=500, batch_size=32, number_heads=6, number_layers=6, dropout=0.1, learning_rate=3e-4, eval_interval=500, epochs=2000):
        self.__embedding_dim = max((1, int(embedding_dim))) if type(embedding_dim) in (bool, int, float) else 384
        self.__block_size = max((1, int(block_size))) if type(block_size) in (bool, int, float) else 500
        self.__batch_size = max((1, int(batch_size))) if type(batch_size) in (bool, int, float) else 32
        self.__number_heads = max((1, int(number_heads))) if type(number_heads) in (bool, int, float) else 6
        self.__number_layers = max((1, int(number_layers))) if type(number_layers) in (bool, int, float) else 6
        self.dropout = max((0, float(dropout))) if type(dropout) in (bool, int, float) else 0.1
        self.__learning_rate = max((0, float(learning_rate))) if type(learning_rate) in (bool, int, float) else 3e-4
        self.__eval_interval = max((1, int(eval_interval))) if type(eval_interval) in (bool, int, float) else 500
        self.__epochs = max((1, int(epochs))) if type(epochs) in (bool, int, float) else 2000
        from torch import cuda, device, backends
        from torch.utils.data import Dataset, DataLoader
        from torch.nn import Module, functional as Function, utils
        from torch import nn as artificial_neural_network, triu, ones
        from torch import tensor, no_grad, int64, multinomial, cat, topk, where, sort, cumsum, zeros_like, bool as torch_bool, save, load
        from tiktoken import get_encoding
        from json import load as json_load
        from torch import optim
        from tqdm import tqdm
        from os import path as os_path, makedirs as os_makedirs
        if cuda.is_available(): local_device = device('cuda')
        elif backends.mps.is_available(): local_device = device('mps')
        else: local_device = device('cpu')
        self.__Dataset = Dataset
        self.__Module = Module
        self.__neural_network = artificial_neural_network
        self.__tensor = tensor
        self.__triu = triu
        self.__ones = ones
        self.__no_grad = no_grad
        self.__device = local_device
        self.__Function = Function
        self.__int64 = int64
        self.__multinomial = multinomial
        self.__cat = cat
        self.__topk = topk
        self.__where = where
        self.__sort = sort
        self.__cumsum = cumsum
        self.__zeros_like = zeros_like
        self.__bool = torch_bool
        self.__get_encoding = get_encoding
        self.__json_load = json_load
        self.__DataLoader = DataLoader
        self.__optim = optim
        self.__utils = utils
        self.__tqdm = tqdm
        self.__os_path = os_path
        self.__os_makedirs = os_makedirs
        self.__save = save
        self.__load = load
        self.__model = None
        self.__encode = None
        self.__decode = None
        self.__end_tag = None
        self.__string = ''
        self.__vocab_size = 0
        self.__char_to_idx = {}
        self.__idx_to_char = {}
        self.__tokenizer = 'gpt'
        self.__optimizer = None
        self.__train = False
        self.parameters_number = 0
        class TextDataset(self.__Dataset):
            def __init__(self, data={}, block_size=0): self.data, self.block_size = data, block_size
            def __len__(self): return len(self.data) - self.block_size
            def __getitem__(self, index=0):
                input_sequence = self.data[index:index + self.block_size]
                target_sequence = self.data[index + 1:index + self.block_size + 1]
                return input_sequence, target_sequence
        class Transformer(self.__Module):
            def __init__(self, outer=None, vocab_size=0, embedding_dim=0, number_heads=0, number_layers=0, dropout=None, block_size=0):
                super().__init__()
                self.outer = outer
                self.positional_encoding = outer._GPTModel__neural_network.Parameter(outer._GPTModel__tensor([]).new_zeros(1, block_size, embedding_dim))
                self.dropout = outer._GPTModel__neural_network.Dropout(dropout)
                self.input_embedding = outer._GPTModel__neural_network.Embedding(vocab_size, embedding_dim)
                self.multi_head_attention = outer._GPTModel__neural_network.TransformerDecoder(outer._GPTModel__neural_network.TransformerDecoderLayer(d_model=embedding_dim, nhead=number_heads, dropout=dropout), num_layers=number_layers)
                self.output_function = outer._GPTModel__neural_network.Linear(embedding_dim, vocab_size)
                self.block_size = block_size
            def forward(self, input_tensor=[]):
                outer = self.outer
                batch_size, sequence_length = input_tensor.size()
                positions = self.positional_encoding[:, :sequence_length, :].to(input_tensor.device)
                output_embedding = self.dropout(self.input_embedding(input_tensor) + positions)
                transposed = output_embedding.transpose(0, 1)
                masked_multi_head_attention = outer._GPTModel__triu(outer._GPTModel__ones(sequence_length, sequence_length, device=input_tensor.device) * float('-inf'), diagonal=1)
                add_and_norm = self.multi_head_attention(transposed, transposed, tgt_mask=masked_multi_head_attention)
                add_and_norm = add_and_norm.transpose(0, 1)
                return self.output_function(add_and_norm)
        self.__TextDatasets = TextDataset
        self.__Transformers = Transformer
    def __compute_loss(self, loader=[]):
        self.__model.eval()
        total_loss = 0
        with self.__no_grad():
            for input_batch, target_batch in loader:
                input_batch, target_batch = input_batch.to(self.__device), target_batch.to(self.__device)
                logits = self.__model(input_batch)
                loss = self.__Function.cross_entropy(logits.view(-1, logits.size(-1)), target_batch.view(-1))
                total_loss += loss.item()
        return total_loss / len(loader)
    def __format_params(self, number_params=0):
        if number_params < 1_000: return f'{number_params}U'
        elif number_params < 1_000_000: return f'{number_params // 1_000}K'
        elif number_params < 1_000_000_000: return f'{number_params // 1_000_000}M'
        elif number_params < 1_000_000_000_000: return f'{number_params // 1_000_000_000}B'
        else: return f'{number_params // 1_000_000_000_000}T'
    def __get_found_end_tag(self, decoded_token='', decoded_tokens='', limits=[]):
        if self.__end_tag is None: return False
        decoded_token, decoded_tokens, limits = str(decoded_token).strip(), str(decoded_tokens).strip(), list(limits)
        for limit in ['']+limits+[' ']:
            if decoded_token.endswith(limit+self.__end_tag) or decoded_tokens.endswith(limit+self.__end_tag): return True
            elif decoded_token.endswith(limit+self.__end_tag[0]) or decoded_tokens.endswith(limit+self.__end_tag[0]): return True
        return False
    def __generate_tokens_x(self, prompt='', max_tokens=500, temperature=1.0):
        self.__model.eval()
        encoded_prompt = self.__encode(prompt)
        input_tensor = self.__tensor(encoded_prompt, dtype=self.__int64).unsqueeze(0).to(self.__device)
        limits = ('.', '\n', '!', '?', ';')
        with self.__no_grad():
            tokens_generated, decoded_tokens = 0, ''
            while True:
                conditioned_input = input_tensor[:, -self.__block_size:] if input_tensor.size(1) > self.__block_size else input_tensor
                logits = self.__model(conditioned_input)
                logits = logits[:, -1, :] / temperature
                output_probabilities = self.__Function.softmax(logits, dim=-1)
                shifted_right = self.__multinomial(output_probabilities, num_samples=1)
                input_tensor = self.__cat((input_tensor, shifted_right), dim=1)
                token = shifted_right.item()
                decoded_token, found_end_tag = self.__decode([token]), False
                if tokens_generated == 0 and '\n' in decoded_token: continue
                tokens_generated += 1
                decoded_tokens += decoded_token
                found_end_tag = self.__get_found_end_tag(decoded_token=decoded_token, decoded_tokens=decoded_tokens, limits=limits)
                if found_end_tag and decoded_token.endswith(self.__end_tag[0]): decoded_token = decoded_token[:-1]
                yield decoded_token
                if found_end_tag or ((tokens_generated >= max_tokens) and (decoded_token[-1] in limits)) or (tokens_generated >= (max_tokens*2)): break
    def __generate_tokens_y(self, prompt='', max_tokens=500, temperature=1.0, top_k=50, top_p=0.9):
        self.__model.eval()
        encoded_prompt = self.__encode(prompt)
        input_tensor = self.__tensor(encoded_prompt, dtype=self.__int64).unsqueeze(0).to(self.__device)
        limits = ('.', '\n', '!', '?', ';')
        with self.__no_grad():
            tokens_generated, decoded_tokens = 0, ''
            while True:
                conditioned_input = (input_tensor[:, -self.__block_size:] if input_tensor.size(1) > self.__block_size else input_tensor)
                logits = self.__model(conditioned_input)
                logits = logits[:, -1, :] / temperature
                if top_k > 0:
                    top_k = min(top_k, logits.size(-1))
                    value, _ = self.__topk(logits, top_k)
                    thresh = value[:, -1].unsqueeze(-1)
                    logits = self.__where(logits < thresh, self.__tensor(float('-inf')).to(logits), logits)
                if top_p < 1.0:
                    sorted_logits, sorted_index = self.__sort(logits, dim=-1, descending=True)
                    sorted_probabilities = self.__Function.softmax(sorted_logits, dim=-1)
                    cumulative_probabilities = self.__cumsum(sorted_probabilities, dim=-1)
                    sorted_mask = cumulative_probabilities > top_p
                    sorted_mask[:, 0] = False
                    mask = self.__zeros_like(logits, dtype=self.__bool)
                    mask.scatter_(-1, sorted_index, sorted_mask)
                    logits = logits.masked_fill(mask, float('-inf'))
                output_probabilities = self.__Function.softmax(logits, dim=-1)
                shifted_right = self.__multinomial(output_probabilities, num_samples=1)
                input_tensor = self.__cat((input_tensor, shifted_right), dim=1)
                token = shifted_right.item()
                decoded_token, found_end_tag = self.__decode([token]), False
                if tokens_generated == 0 and '\n' in decoded_token: continue
                tokens_generated += 1
                decoded_tokens += decoded_token
                found_end_tag = self.__get_found_end_tag(decoded_token=decoded_token, decoded_tokens=decoded_tokens, limits=limits)
                if found_end_tag and decoded_token.endswith(self.__end_tag[0]): decoded_token = decoded_token[:-1]
                yield decoded_token
                if found_end_tag or ((tokens_generated >= max_tokens) and (decoded_token[-1] in limits)) or (tokens_generated >= (max_tokens*2)): break
    def __generate_tokens(self, prompt='', max_tokens=500, temperature=1.0, top_k=0, top_p=1.0):
        prompt = '?' if len(str(prompt).strip()) < 1 else str(prompt).strip()
        def get_last_n_tokens(text='', n=0):
            if self.__tokenizer == 'sapi': return text[-n:]
            else:
                encoding = self.__get_encoding('gpt2')
                tokens = encoding.encode(text)
                last_n_tokens = tokens[-n:]
                truncated_text = encoding.decode(last_n_tokens)
                return truncated_text
        prompt = get_last_n_tokens(text=prompt, n=self.__block_size)
        if top_k > 0 or top_p < 1.0: return self.__generate_tokens_y(prompt=prompt, max_tokens=max_tokens, temperature=temperature, top_k=top_k, top_p=top_p)
        else: return self.__generate_tokens_x(prompt=prompt, max_tokens=max_tokens, temperature=temperature)
    def train(self, dataset_path='', string='', precision=0.9, tokenizer='gpt', context_window=500, end_tag=None, validate=0.0, progress=True):
        try:
            training_metrics = {'val_loss': 0.0, 'loss': 0.0, 'generalization_rate': 0.0, 'precision': 0.0}
            dataset_path = str(dataset_path).strip()
            string = str(string).strip()
            precision = min((1.0, max((0.0, float(precision))))) if type(precision) in (bool, int, float) else 0.9
            tokenizer = str(tokenizer).lower().strip()
            self.__block_size = max((1, int(context_window))) if type(context_window) in (bool, int, float) else 500
            if end_tag is not None and self.__end_tag is None: self.__end_tag = str(end_tag)
            validate = min((1.0, max((0.0, float(validate))))) if type(validate) in (bool, int, float) else 0.0
            progress = bool(progress) if type(progress) in (bool, int, float) else True
            if tokenizer not in ('sapi', 'gpt'): tokenizer = 'gpt'
            self.__string = str(self.__string+'\n\n'+string).strip()
            loss_limit = min(1.0, max(0.0, 1.0 - precision))
            is_txt, is_json, text_data = dataset_path.endswith('.txt'), dataset_path.endswith('.json'), ''
            def prepare_json(json_data={}):
                if type(json_data) == dict: pairs = json_data[list(json_data.keys())[0]]
                else: pairs = json_data
                if self.__end_tag is None: self.__end_tag = '<|end|>'
                return '\n\n'.join([str(pair[list(pair.keys())[0]]+'\n'+pair[list(pair.keys())[1]]).replace(self.__end_tag, '').strip()+self.__end_tag for pair in pairs])                
            def is_web_address(url_path=''):
                url_path = str(url_path).lower().strip()
                return url_path.startswith('https://') or url_path.startswith('http://') or url_path.startswith('www.')
            _is_web_address = is_web_address(url_path=dataset_path)
            if _is_web_address:
                is_json = True if '.json' in dataset_path.lower() else False
                def read_remote_file(url_path=''):
                    from urllib.request import urlopen
                    with urlopen(url_path) as response: return str(response.read().decode('utf-8', errors='replace').replace('\r\n', '\n').replace('\r', '\n')).strip()
                text_data = read_remote_file(url_path=dataset_path)
                if is_json:
                    def load_json(string_content=''):
                        json_content = {}
                        string_content = str(string_content)
                        try:
                            from json import loads
                            json_content = loads(string_content)
                        except:
                            from ast import literal_eval
                            json_content = literal_eval(string_content)
                        return json_content
                    json_data = load_json(string_content=text_data)
                    text_data = prepare_json(json_data=json_data)
            else:
                if not is_txt and not is_json and len(self.__string) < 1: raise ValueError('Unsupported file format. Use .txt or .json.')
                if is_txt:
                    with open(dataset_path, 'r', encoding='utf-8') as file: text_data = str(file.read()).strip()
                elif is_json:
                    with open(dataset_path, 'r', encoding='utf-8') as file: json_data = self.__json_load(file)
                    text_data = prepare_json(json_data=json_data)
            if len(self.__string) > 0: text_data += '\n\n' + self.__string
            text_data = text_data.strip()
            if tokenizer == 'sapi':
                chars = sorted(list(set(text_data)))
                self.__vocab_size = len(chars)
                self.__char_to_idx = {char: index for index, char in enumerate(chars)}
                self.__idx_to_char = {index: char for index, char in enumerate(chars)}
                self.__encode = lambda string: [self.__char_to_idx[char] for char in string]
                self.__decode = lambda indices: ''.join([self.__idx_to_char[index] for index in indices])
            else:
                encode = self.__get_encoding('gpt2')
                self.__vocab_size = encode.n_vocab
                self.__encode = encode.encode
                self.__decode = encode.decode
            data = self.__tensor(self.__encode(text_data), dtype=self.__int64)
            if validate > 0:
                split_point = int((1-validate) * len(data))
                train_data, validation_data = data[:split_point], data[split_point:]
                minimum_length = min(len(train_data), len(validation_data))
                if minimum_length >= 2:
                    desired_block_size = int(context_window) if context_window else 500
                    self.__block_size = max(1, min(desired_block_size, minimum_length - 1))
                else: self.__block_size = 1
            else:
                train_data = data
                data_length = len(train_data)
                self.__block_size = max(1, min(self.__block_size, data_length - 1))
            self.__tokenizer = tokenizer
            train_dataset = self.__TextDatasets(train_data, self.__block_size)
            if validate > 0: validation_dataset = self.__TextDatasets(validation_data, self.__block_size)
            train_loader = self.__DataLoader(train_dataset, batch_size=self.__batch_size, shuffle=True)
            if validate > 0: validation_loader = self.__DataLoader(validation_dataset, batch_size=self.__batch_size, shuffle=False)
            self.__model = self.__Transformers(self, self.__vocab_size, self.__embedding_dim, self.__number_heads, self.__number_layers, self.dropout, self.__block_size).to(self.__device)
            self.__optimizer = self.__optim.AdamW(self.__model.parameters(), lr=self.__learning_rate)
            scheduler, feed_forward = self.__optim.lr_scheduler.ReduceLROnPlateau(self.__optimizer, mode='min', factor=0.5, patience=3), True
            Nx, last_validation_loss, step, best_val_loss = 0, 1.0, 0, float('inf')
            string_precision = f'{precision:.4f}'.ljust(5, '0')
            formatted_string = '{desc}: {percentage:3.0f}%|{bar:10}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt:>9}]'
            while feed_forward:
                self.__model.train()
                loss_item, total_train_loss = 1.0, 1.0
                epoch = str(Nx+1).rjust(10, '0')
                for input_batch, target_batch in train_loader:
                    input_batch, target_batch = input_batch.to(self.__device), target_batch.to(self.__device)
                    logits = self.__model(input_batch)
                    loss = self.__Function.cross_entropy(logits.view(-1, logits.size(-1)), target_batch.view(-1))
                    self.__optimizer.zero_grad()
                    loss.backward()
                    self.__utils.clip_grad_norm_(self.__model.parameters(), 1.0)
                    self.__optimizer.step()
                    loss_item = loss.item()
                    total_train_loss += loss_item
                    last_validation_loss = validation_loss = self.__compute_loss(validation_loader) if validate > 0 else 1.0
                    training_metrics['generalization_rate'] = min((1.0, max((0.0, 1.0-validation_loss))))
                    if step > 0 and step % self.__eval_interval == 0:
                        scheduler.step(validation_loss)
                        if validation_loss < best_val_loss: best_val_loss = validation_loss
                    step += 1
                current_precision = min(1.0, max(0.0, 1.0 - loss_item))
                average_train_loss = total_train_loss / max((1, len(train_loader)))
                if current_precision >= precision or average_train_loss <= loss_limit or Nx >= self.__epochs:
                    training_metrics['loss'] = loss_item if current_precision >= precision else average_train_loss
                    training_metrics['precision'] = current_precision
                    if progress:
                        description = f'Finalization of backpropagations... current precision is '+f'{current_precision:.4f}'.ljust(5, '0')+f'; aiming for precision >= {string_precision} in training'
                        self.__tqdm(train_loader, desc=description, unit='it', unit_scale=True, unit_divisor=1000, smoothing=0.1, bar_format=formatted_string).update(len(train_loader))
                        print()
                    break
                elif progress:
                    description = f'Backpropagation epoch: {epoch} - current precision is '+f'{current_precision:.4f}'.ljust(5, '0')+f'; aiming for precision >= {string_precision} in training'
                    train_loader = self.__tqdm(train_loader, desc=description, unit='it', unit_scale=True, unit_divisor=1000, smoothing=0.1, bar_format=formatted_string)
                Nx += 1
            training_metrics['val_loss'] = best_val_loss if best_val_loss < 1.0 else min((1.0, max((0.0, last_validation_loss))))
            self.__train = True
            return training_metrics
        except Exception as error:
            print('ERROR in train: ' + str(error))
            try: return training_metrics
            except: return {'val_loss': 1.0, 'loss': 1.0, 'generalization_rate': 0.0, 'precision': 0.0}
    def saveModel(self, model_path='', progress=True):
        try:
            model_path = str(model_path).strip()
            progress = bool(progress) if type(progress) in (bool, int, float) else True
            if self.__model is None: raise ValueError('Model is not initialized. Call train or loadModel first.')
            self.parameters_number = sum(parameters.numel() for parameters in self.__model.parameters())
            formatted_params = self.__format_params(self.parameters_number)
            if len(model_path) > 0:
                directory, file_name = self.__os_path.split(model_path)
                if not file_name: file_name = 'model.gpt'
                elif not file_name.endswith('.gpt'): file_name += '.gpt'
            else: directory, file_name = str(model_path), 'model.gpt'
            if directory and not self.__os_path.exists(directory): self.__os_makedirs(directory)
            save_path = self.__os_path.join(directory, file_name)
            save_dict = {
                'tokenizer': str(self.__tokenizer).lower().strip(),
                'embedding_dim': max((1, int(self.__embedding_dim))) if type(self.__embedding_dim) in (bool, int, float) else -1,
                'vocab_size': max((0, int(self.__vocab_size))) if type(self.__vocab_size) in (bool, int, float) else 0,
                'block_size': max((1, int(self.__block_size))) if type(self.__block_size) in (bool, int, float) else -1,
                'end_tag': str(self.__end_tag) if type(self.__end_tag) is not None else '',
                'number_heads': max((1, int(self.__number_heads))) if type(self.__number_heads) in (bool, int, float) else -1,
                'number_layers': max((1, int(self.__number_layers))) if type(self.__number_layers) in (bool, int, float) else -1,
                'dropout': max((0, int(self.dropout))) if type(self.dropout) in (bool, int, float) else 0.1,
                'parameters_number': max((0, int(self.parameters_number))) if type(self.parameters_number) in (bool, int, float) else 0,
                'architecture_type': 'gpt_model',
                'model_state_dict': self.__model.state_dict(),
                'fine_tuning': [],
                'precision': 1.0

            }
            if self.__tokenizer == 'sapi':
                save_dict['char_to_idx'] = self.__char_to_idx if type(self.__char_to_idx) == dict else {}
                save_dict['idx_to_char'] = self.__idx_to_char if type(self.__idx_to_char) == dict else {}
            if progress:
                for _ in self.__tqdm(range(10), desc=f'Saving model with {formatted_params} parameters', leave=False): self.__save(save_dict, save_path)
            else: self.__save(save_dict, save_path)
            return True
        except Exception as error:
            print('ERROR in saveModel: ' + str(error))
            return False
    def loadModel(self, model_path='', progress=True):
        try:
            model_path = str(model_path).strip()
            progress = bool(progress) if type(progress) in (bool, int, float) else True
            if len(model_path) > 0:
                directory, file_name = self.__os_path.split(model_path)
                if not file_name: file_name = 'model.gpt'
                elif not file_name.endswith('.gpt'): file_name += '.gpt'
            else: directory, file_name = str(model_path), 'model.gpt'
            model_file = self.__os_path.join(directory, file_name)
            if progress:
                for _ in self.__tqdm(range(10), desc='Loading model', leave=False): checkpoint = self.__load(model_file, map_location=self.__device)
            else: checkpoint = self.__load(model_file, map_location=self.__device)
            try: self.__tokenizer = str(checkpoint['tokenizer']).lower().strip()
            except: self.__tokenizer = 'gpt'
            try: self.__embedding_dim = max((1, int(checkpoint['embedding_dim']))) if checkpoint['embedding_dim'] != -1 else None
            except: self.__embedding_dim = None
            try: self.__vocab_size = max((0, int(checkpoint['vocab_size']))) if type(checkpoint['vocab_size']) in (bool, int, float) else 0
            except: self.__vocab_size = 0
            try: self.__block_size = max((1, int(checkpoint['block_size']))) if type(checkpoint['block_size']) != -1 else None
            except: self.__block_size = None
            try: self.__end_tag = str(checkpoint['end_tag'])
            except: self.__end_tag = ''
            try: self.__number_heads = max((1, int(checkpoint['number_heads']))) if type(checkpoint['number_heads']) != -1 else None
            except: self.__number_heads = None
            try: self.__number_layers = max((1, int(checkpoint['number_layers']))) if type(checkpoint['number_layers']) != -1 else None
            except: self.__number_layers = None
            try: self.dropout = max((0, float(checkpoint['dropout']))) if type(checkpoint['dropout']) in (bool, int, float) else 0.1
            except: self.dropout = 0.1
            try: self.parameters_number = max((0, int(checkpoint['parameters_number']))) if type(checkpoint['parameters_number']) in (bool, int, float) else 0
            except: self.parameters_number = 0
            if self.__tokenizer == 'sapi':
                try: self.__char_to_idx = dict(checkpoint['char_to_idx'])
                except: self.__char_to_idx = {}
                try: self.__idx_to_char = dict(checkpoint['idx_to_char'])
                except: self.__idx_to_char = {}
                self.__encode = lambda string: [self.__char_to_idx[char] for char in string]
                self.__decode = lambda indexes: ''.join([self.__idx_to_char[index] for index in indexes])
            else:
                encode = self.__get_encoding('gpt2')
                self.__encode = encode.encode
                self.__decode = encode.decode
            if len(self.__end_tag) < 1: self.__end_tag = None
            self.__model = self.__Transformers(outer=self, vocab_size=self.__vocab_size, embedding_dim=self.__embedding_dim, number_heads=self.__number_heads, number_layers=self.__number_layers, dropout=self.dropout, block_size=self.__block_size).to(self.__device)
            state_dict = checkpoint['model_state_dict']
            self.__model.load_state_dict(state_dict)
            self.__optimizer, self.__train = None, True
            return True
        except Exception as error:
            print('ERROR in loadModel: ' + str(error))
            return False
    def addFit(self, prompt='', answer=''):
        try:
            prompt = str(prompt).strip()
            answer = str(answer).strip()
            if not self.__train:
                if self.__end_tag is None: self.__end_tag = '<|end|>'
                self.__string += prompt+'\n'+answer+self.__end_tag+'\n\n'
            else:
                if self.__model is None: raise ValueError('Model is not initialized. Call train or loadModel first.')
                if self.__optimizer is None: self.__optimizer = self.__optim.AdamW(self.__model.parameters(), lr=self.__learning_rate)
                if self.__end_tag is None: formatted = prompt+'\n'+answer+'\n\n'
                else: formatted = prompt+'\n'+answer+self.__end_tag+'\n\n'
                encoded = self.__encode(formatted)
                if len(encoded) > self.__block_size: encoded = encoded[:self.__block_size]
                input_tensor = self.__tensor(encoded[:-1], dtype=self.__int64).unsqueeze(0).to(self.__device)
                target_tensor = self.__tensor(encoded[1:], dtype=self.__int64).unsqueeze(0).to(self.__device)
                self.__model.train()
                logits = self.__model(input_tensor)
                loss = self.__Function.cross_entropy(logits.view(-1, logits.size(-1)), target_tensor.view(-1))
                self.__optimizer.zero_grad()
                loss.backward()
                self.__utils.clip_grad_norm_(self.__model.parameters(), 1.0)
                self.__optimizer.step()
            return True
        except Exception as error:
            print('ERROR in addFit: ' + str(error))
            return False
    def predict(self, prompt='', max_tokens=500, temperature=0.5, top_k=0, top_p=1.0, stream=False):
        try:
            prompt = str(prompt).strip()
            max_tokens = max((1, int(max_tokens))) if type(max_tokens) in (bool, int, float) else 500
            temperature = max((0, float(temperature))) if type(temperature) in (bool, int, float) else 0.5
            top_k = max((0, int(top_k))) if type(top_k) in (bool, int, float) else 0
            top_p = min((1.0, max((0.0, int(top_p))))) if type(top_p) in (bool, int, float) else 1.0
            stream = bool(stream) if type(stream) in (bool, int, float) else False
            if self.__model is None: raise ValueError('Model is not initialized. Call train or loadModel first.')
            if stream: return self.__generate_tokens(prompt=prompt, max_tokens=max_tokens, temperature=temperature, top_k=top_k, top_p=top_p)
            tokens = list(self.__generate_tokens(prompt=prompt, max_tokens=max_tokens, temperature=temperature, top_k=top_k, top_p=top_p))
            return ''.join(tokens)
        except Exception as error:
            print('ERROR in predict: ' + str(error))
            return ''
    def print_predict(self, prompt='', max_tokens=500, temperature=0.5, top_k=0, top_p=1.0, stream=False):
        try:
            prompt = str(prompt).strip()
            max_tokens = max((1, int(max_tokens))) if type(max_tokens) in (bool, int, float) else 500
            temperature = max((0, float(temperature))) if type(temperature) in (bool, int, float) else 0.5
            top_k = max((0, int(top_k))) if type(top_k) in (bool, int, float) else 0
            top_p = min((1.0, max((0.0, int(top_p))))) if type(top_p) in (bool, int, float) else 1.0
            stream = bool(stream) if type(stream) in (bool, int, float) else False
            if self.__model is None: raise ValueError('Model is not initialized. Call train or loadModel first.')
            if stream:
                [print(token, end='', flush=True) for token in self.__generate_tokens(prompt=prompt, max_tokens=max_tokens, temperature=temperature, top_k=top_k, top_p=top_p)]
                print()
            else: print(self.predict(prompt=prompt, max_tokens=max_tokens, temperature=temperature, stream=stream))
        except Exception as error:
            print('ERROR in print_predict: ' + str(error))
# This is a standard code of a GPT (Generative Pre-trained Transformer) model, developed by Sapiens Technology®️,
# which faithfully follows the mathematical structure of the article “Attention Is All You Need” for the construction of the Transformer architecture
# used in the pattern recognition of the model that is saved. Some optimizations that do not influence the Transformer architecture
# were applied only to facilitate the adjustments of the parameters and variables of the training, saving, loading, fine-tuning and inference of the pre-trained model.
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
